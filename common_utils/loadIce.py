# coding:utf-8
import os
import sys

# 将PRC接口模块加入加载模块路径

if getattr(sys, 'frozen', False):
    # The application is frozen
    current_dir = os.path.split(os.path.realpath(sys.executable))[0]
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    current_dir = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(current_dir)
ice_dir = os.path.join(current_dir, '..', 'rpc_ice', 'py')
sys.path.append(ice_dir)
