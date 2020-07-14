#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 14:00:14 2019

@author: python
"""
import socket , os

def socket_bind_recv(socket_fn, cmd_handler):
    """
    基于bsd系统的进程间socket通信，接受消息，处理消息
    :param socket_fn: socket文件名称
    :param cmd_handler: cmd处理函数，callable类型
    """
    if not callable(cmd_handler):
        print('socket_bind_recv cmd_handler must callable!')

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_fn)
    server.listen(0)
    while True:
        connection, _ = server.accept()
        socket_cmd = connection.recv(1024).decode()
        # 把接收到的socket传递给外部对应的处理函数
        cmd_handler(socket_cmd)
        connection.close()


def socket_send_msg(socket_fn, msg):
    """
    基于bsd系统的进程间socket通信，发送消息
    :param socket_fn: : socket文件名称
    :param msg: 字符串类型需要传递的数据，不需要encode，内部进行encode
    """
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_fn)
    client.send(msg.encode())
    client.close()


def show_msg(title, msg):
    """
    使用osascript脚步提示弹窗，主要用在长时间且耗时的任务中，提示重要问题信息
    :param title: 弹窗标题
    :param msg: 弹窗信息
    """
    msg_cmd = 'osascript -e \'display notification "%s" with title "%s"\'' % (msg, title)
    os.system(msg_cmd)


def fold_free_size_mb(folder):
    """
    mac os下剩余磁盘空间获取
    :param folder: 目标目录
    :return: 返回float，单位mb
    """
    st = os.statvfs(folder)
    return st.f_bavail * st.f_frsize / 1024 / 1024


"""
'AF_INET' 地址是 (主机, 端口)  形式的元组类型，其中 主机 是一个字符串，端口 是整数。

'AF_UNIX' 地址是文件系统上文件名的字符串。

'AF_PIPE' 是这种格式的字符串 r'\.\pipe{PipeName}' 。如果要用 Client() 连接到一个名为 ServerName 的远程命名管道，应该替换为使用 r'\ServerName\pipe{PipeName}' 这种格式。
"""

"""
服务器必须执行序列socket()， bind()，listen()，accept()（可能重复accept()，以服务一个以上的客户端），
而一个客户端只需要在序列socket()，connect()。另请注意，服务器不在sendall()/ recv()侦听的套接字上，而是/ 返回的新套接字 accept()
"""

HOST = '192.168.0.103'                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(20)
            if not data:
                break
            conn.sendall(data + b' response')