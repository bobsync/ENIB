#include<stdio.h>
#include<winsock2.h>
#include <string>
#include <algorithm>
#include <iostream>
#include <list>
#include <vector>
#include <map>
#include <fstream>
#include <iostream>
#include <winsock.h>
#include <ws2tcpip.h>

#pragma warning(disable : 4996)
#pragma comment(lib,"ws2_32.lib") //Winsock Library

#define SERVER_PORT 11000	//The port on which to listen for incoming data
#define BUFF_LEN 10000

struct  destination {
    sockaddr_in adress;
    int l;
};

int main()
{
    //  Create Map+
    std::map<std::string, std::list<destination>> whithBoard;

    //---- create UDP socket ----
    WSAData data;
    WSAStartup(MAKEWORD(2, 2), &data);
    int sock, length, n;
    int fromlen;
    struct sockaddr_in server;
    struct sockaddr_in from;

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) printf("Opening socket");
    length = sizeof(server);
    memset(&server, 0, length);
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(SERVER_PORT);
    if (bind(sock, (struct sockaddr*)&server, length) < 0) printf("Error binding");
    fromlen = sizeof(struct sockaddr_in);
    /*--*/
    char ac[80];
    if (gethostname(ac, sizeof(ac)) == SOCKET_ERROR) {
        std::cout << "Error " << WSAGetLastError() <<
            " when getting local host name.";
        return 1;
    }
    std::cout << "Host name is " << ac << ".";
    struct hostent* phe = gethostbyname(ac);
    if (phe == 0) {
        std::cout << "Yow! Bad host lookup.";
        return 1;
    }
    for (int i = 0; phe->h_addr_list[i] != 0; ++i) {
        struct in_addr addr;
        memcpy(&addr, phe->h_addr_list[i], sizeof(struct in_addr));
        std::cout << "Address " << i << ": " << inet_ntoa(addr) << ", ";
    }
    // Log file preparation
    time_t tmm = time(0);
    char* dt = ctime(&tmm);
    tm* ltm = localtime(&tmm);
    std::string a ="whiteboard/x64/Debug/logs/log" + std::to_string(ltm->tm_mday) + 'm' + std::to_string(ltm->tm_hour) + 'h' + std::to_string(ltm->tm_min)+".txt";
    std::ofstream file(a.c_str());
    if (file)
    {
        file << dt << std::endl;
    }
    else
    {
        std::cout << "ERREUR: File not open" << std::endl;
    }
    int nMessage = 0;
    printf("host waiting for an UDP message on port %hu ...\n", SERVER_PORT);
    char buff[BUFF_LEN] = { 0 };

    for (;;) // as long as dialog can go on...
    {
        for (int i = 0; i < BUFF_LEN; i++) {
            buff[i] = '\0';
        }
         
        //---- receive and display request and source address/port ----
        n = recvfrom(sock, buff, BUFF_LEN, 0, (struct sockaddr*)&from, &fromlen);
        
        std::string request = std::string(buff);
        std::cout << request <<"\n";

        if (request.substr(0, 10).compare("Subscribe:") == 0) {// check for "Subscribe:" at the start of the request
            destination c;
            c.adress = from;
            c.l = fromlen;
            std::string topic = request.substr(10);
            if (whithBoard.count(topic) == 0) {
                whithBoard[topic].push_back(c);
            }
            else {
                bool contain = false;
                std::list<destination> l = whithBoard.at(topic);
                for (std::list<destination>::iterator it = l.begin(); it != l.end(); ++it) {//check that the key is not already present
                    if (from.sin_port == it->adress.sin_port) {
                        contain = true;
                    }
                }
                if (!contain) {// add the key
                    std::list<destination> l2 = whithBoard.at(topic);
                    l2.push_back(c);
                    whithBoard[topic] = l2;
                }
                else {
                    std::cout << "Module deja abonne au topic" << std::endl;
                }
            }
        }

        else {// if this is not a first post (not a Subscribe:)
            std::size_t i = request.find_first_of(":");
            std::string topic = request.substr(0, i);
            if (whithBoard.count(topic) > 0) {
                std::list<destination> l = whithBoard.at(topic);
                std::string s = request;
                char* char_arr;
                char_arr = &s[0];
                    for (std::list<destination>::iterator it = l.begin(); it != l.end(); ++it) {
                        //std::cout << "taille de la reponse " << s.length() << std::endl;
                        n = sendto(sock, char_arr, s.length(), 0, (struct sockaddr*)&it->adress, it->l);
                    }

            }
            else {
                std::string s2 = request.substr(0, i + 1);
                char* char_arr2;
                char_arr2 = &s2[0];
                if (char_arr2[0] != '\0') {  // Check if char_arr2 is not an empty string
                    std::cout << "Le type \"" << char_arr2 << "\" n'as pas encore ete reclame\n";
                }
            }

        }
        // Write in the log file
        tmm = time(0);
        tm* ltm = localtime(&tmm);
        file << "<" << ltm->tm_hour << ":" << ltm->tm_min << ":" << ltm->tm_sec << " n:" << nMessage << " From" << " port:" << from.sin_port << " >\"" << buff << "\"" << std::endl;
        nMessage = nMessage + 1;
    }


    closesocket(sock);
    WSACleanup();
    return 0;
}