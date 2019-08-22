import os
import json
import subprocess
import threading
import sys
import time

try:
    from common_utils import xlogging
except:
    sys.path.append('..')  # 工程目录加入
    from common_utils import xlogging

_logger = xlogging.getLogger(__name__)

g_agent_path = os.path.join("/opt/ClwDbMgr", "ClwOraAgent")
g_config_path = os.path.join(g_agent_path, "usrcfg.json")
g_backup_json = os.path.join(g_agent_path, "backup.json")
g_backup_logs = os.path.join(g_agent_path, "orabackup.log")
g_result_json = os.path.join(g_agent_path, "result.json")


def log_err(msg):
    _logger.error(msg)
    print("[info] {}".format(msg))


def log_info(msg):
    _logger.info(msg)
    print("[err] {}".format(msg))


def log_dbg(msg):
    print("[dbg] {}".format(msg))


def read_josn_data(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
            return data
    except Exception as e:
        log_err('[read_josn_data] except={}'.format(e))
        return None


def write_json_data(raw, path):
    retval = False
    data = json.dumps(raw) + "\n"
    try:
        with open(path, "wt") as f:
            f.write(data)
        retval = True
    except Exception as e:
        log_err('[write_json_data] except={}'.format(e))
    return retval


def exec_command(cmd, current=None):
    stdmsg = []
    stderr = []
    log_dbg("[exec_command] cmd={}".format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=current,
                         stderr=subprocess.PIPE)
    p.wait()

    for line in p.stdout:
        stdmsg.append(line.rstrip())

    for line in p.stderr:
        stderr.append(line.rstrip())

    return p.returncode, stdmsg, stderr


class oraworker(object):
    def __init__(self, args_dict, raw_input):
        self.bkptag = ""
        self.finish = False
        self.success = False

    def bkp_thread(self):
        try:
            log_info('[bkp_thread] start')

            if os.path.exists(g_result_json):
                os.remove(g_result_json)

            full = os.path.join(g_agent_path, "ClwOraAgent")
            sub = "{} jobtype=backup workdir={}".format(full, g_agent_path)
            cmd = "su - oracle -c '{}'  > {} 2>&1 &".format(sub, g_backup_logs)
            retval = exec_command(cmd)
            if not retval:
                log_err('[bkp_thread] exec_command failed,cmd={}'.format(cmd))

            while True:
                result = read_josn_data(g_result_json)
                if result:
                    break
                time.sleep(5)

            code = result.get("exitcode")
            if code != 0:
                log_err('[bkp_thread] failed code={}'.format(code))
                return

            self.success = True

            log_info('[bkp_thread] success')

        except Exception as e:
            log_err('[bkp_thread] except={}'.format(e))

        finally:
            self.finish = True

        return

    def backup_db(self, args_dict, raw_input):
        log_info('[backup_db] start')

        self.bkptag = args_dict["bkptag"]

        bkpdict = args_dict
        usrcfg = read_josn_data(g_config_path)
        if usrcfg:
            for i in usrcfg:
                bkpdict[i] = usrcfg[i]

        retval = write_json_data(bkpdict, g_backup_json)
        if not retval:
            log_err('[backup_db] write_json_data failed')
            return 'write_json_data failed', None

        self._backup_thread = threading.Thread(target=self.bkp_thread)
        self._backup_thread.setDaemon(True)
        self._backup_thread.start()

        log_info('[backup_db] success')

        return 'ok', b''

    def get_bkpinfo_file(self, args_dict, raw_input):
        file = "bkpinfo_{}.json".format(self.bkptag)
        full = os.path.join(g_agent_path, file)
        log_info("[get_bkpinfo_file] full={}".format(full))
        try:
            with open(full) as f:
                data = f.read()
        except:
            log_err('[get_bkpinfo_file] read bkpinfo failed')

        retval = {"name": file, "data": data}
        return json.dumps(retval), None

    def check_finish(self, args_dict, raw_input):
        data = {"finish": self.finish, "success": self.success}
        retval = json.dumps(data)
        if self.finish:
            log_info("[check_finish] retval={}".format(retval))
        return retval, None

    def cancel_backup(self, args_dict, raw_input):
        return None, None

    def restore_db(self, args_dict, raw_input):
        return None, None

    def cancel_restore(self, args_dict, raw_input):
        return None, None


if __name__ == '__main__':
    ora = oraworker(None, None)
    input = {
        "sbtpath": "libclwobk.so",
        "bkplevel": 0,
        "cumulative": False,
        "bkptag": "clw201906261800",
        "usepipe": False,
        "channels": [
            {
                "userpwd": "sys/f@orcl",
                "envstrs": "sbthost=172.16.32.1",
                "encode": False
            }
        ]
    }

    retstr, retbin = ora.backup_db(input, None)
    if retstr != 'ok':
        log_err("backup_db failed, retstr={}".format(retstr))
        sys.exit(-1)

    success = False
    while True:
        retstr, retbin = ora.check_finish(None, None)
        if len(retstr) <= 0:
            log_err("invalid retstr={}".format(retstr))
            break
        result = json.loads(retstr)
        if result["finish"]:
            success = result["success"]
            log_info("finish sucdess={}".format(success))
            break

        time.sleep(5)

    if success:
        retstr, retbin = ora.get_bkpinfo_file(None, None)
        log_info("bkpinfo={}".format(retstr))

    log_info("exit...")
