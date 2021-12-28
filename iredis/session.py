import os
import sys
import logging
import click
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from .utils import convert_formatted_text_to_bytes
from .config import config
from .style import STYLE
import json
logger = logging.getLogger(__name__)


def is_too_tall(text, max_height):
    if isinstance(text, FormattedText):
        text = convert_formatted_text_to_bytes(text)
    lines = len(text.split(b"\n"))
    return lines > max_height


def write_result(text, max_height=None):
    """
    When config.raw set to True, write text(must be bytes in that case)
    directly to stdout, same if text is bytes.

    :param text: is_raw: bytes or str, not raw: FormattedText
    :is_raw: bool
    """
    logger.info(f"Print result {type(text)}: {text}"[:200])

    # this function only handle bytes or FormattedText
    # if it's str, convert to bytes
    if isinstance(text, str):
        if config.decode:
            text = text.encode(config.decode)
        else:
            text = text.encode()

    # using pager if too tall
    if max_height and config.enable_pager and is_too_tall(text, max_height):
        if isinstance(text, FormattedText):
            text = convert_formatted_text_to_bytes(text)
            os.environ["LESS"] = "-SRX"
        # click.echo_via_pager only accepts str
        if config.decode:
            text = text.decode(config.decode)
        else:
            text = text.decode()
        # TODO current pager doesn't support colors
        click.echo_via_pager(text)
        return

    if isinstance(text, bytes):
        sys.stdout.buffer.write(text)
        sys.stdout.write("\n")
    else:
        print_formatted_text(text, end="", style=STYLE)
        print_formatted_text()


class Session:
    """
    save session
    """
    def __init__(self):
        self,
        self.file = os.path.expanduser('~')+'\\session\\host.json'

    def check_file(self):
        # write_result("session file="+self.file)
        dirname = os.path.dirname(self.file)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if not os.path.exists(self.file):
            t = open(self.file, "w")
            # t.write("{'h': '127.0.0.1', 'p': '6379'}\n")
            t.close()

    def list(self, ctx):
        '''
        return session list with index
        '''
        # exists = os.path.exists(os.path.dirname(file))
        # write_result("--000s--")
        self.check_file()
        # write_result("--2--")
        list = ctx.params['ss']
        arr = []
        # 查看列表
        if list == 'list' or list == 'l':
            f = open(self.file)
            line = f.readline()
            i = 1
            while line:
                if len(line) == 0:
                    break
                if line == '\n':
                    line = f.readline()
                    continue
                v = eval(line)
                # print(v)
                arr.append(' '.join([str(i) + '.', ':'.join([v['h'], v['p']])]))
                i+=1
                # arr.append(line)
                line = f.readline()
            f.close()
            # write_result("--333--")
        write_result('\n'.join(arr))
        return arr

    def getByIdx(self, ctx):
        if not os.path.exists(self.file):
            print("check the sesson list[--ss l] before to do")
            return
        dirname = os.path.dirname(self.file)
        exists = os.path.exists(dirname)
        if not exists:
            os.makedirs(dirname)
            t = open(self.file, "w")
            t.close()

        list = ctx.params['ss']
        try:
            list = int(list)
        except Exception as e:
            logger.exception(e)
            # TODO red error color
            print("(error)", str(e))
            return
        # print(list)
        # 查看列表
        arr = []
        f = open(self.file)
        line = f.readline()
        i = 1
        isFound = False;
        while line:
            # print('---- ', i)
            if len(line) == 0:
                break
            if line == '\n':
                line = f.readline()
                continue
            v = eval(line)
            if list == i:
                ctx.params['h'] = v['h']
                ctx.params['p'] = v['p']
                isFound = True
                return isFound
            # print(v)
            i+=1
            # arr.append(line)
            line = f.readline()
        if not isFound:
            write_result('Invalid Input: ' + str(list))
        return isFound

    def write(self, h_, p_):
        self.check_file()
        f = open(self.file, "r")
        line = f.readline()
        exists = False
        h_ = str(h_)
        p_ = str(p_)
        while line:
            if len(line) == 0:
                break
            if line == '\n':
                line = f.readline()
                continue
            v = eval(line)
            # print(v)
            if v['h'] == h_ and v['p'] == p_:
                exists = True
                break
            line = f.readline()
        f.close()
        if not exists:
            f = open(self.file, "a")
            f.write("{'h': '" + h_ + "', 'p': '" + p_ + "'}\n")
            f.close()

    def load(self, path):
        if not os.path.exists(path):
            print('not founc file')
            return
        with open(path, 'r') as f:
            try:
                json_arr = json.load(f)
            except Exception as e:
                print('Load the file error. The file content may be a not json array format.')
                return
            # print(json_arr)
            for i in json_arr:
                # print(i['host'], i['port'])
                self.write(i['host'], i['port'])

        # f = open(self.file, "r")
        # while fline:
        #     if len(fline) == 0:
        #         break
        #     if fline == '\n':
        #         fline = f.readline()
        #         continue
        #     v = eval(fline)
        #     # print(v)
        #     if v['h'] == h_ and v['p'] == p_:
        #         exists = True
        #         break
        #     fline = f.readline()
        # f.close()
    def getByIdxap2pend(self, ctx, idx):
        file = 'session/host.json'
        # exists = os.path.exists(os.path.dirname(file))
        dirname = os.path.dirname(file)
        exists = os.path.exists(dirname)
        if not exists:
            os.makedirs(dirname)
            t = open(file, "w")
            # t.write("{'h': '127.0.0.1', 'p': '6379'}\n")
            t.close()


        sessionJson = [
            {'h': '127.0.0.1', 'p': '6379'},
            {'h': '192.168.88.155', 'p': '6379'}
        ]
        list = ctx.params['ss']
        # write_result('-----------------;list='+str(sessionJson[0]['h']))
        # 查看列表
        if list == 'list' or list == 'l':
            arr = []
            f = open(file)
            line = f.readline()
            i = 1
            while line:
                if len(line) == 0:
                    break
                if line == '\n':
                    line = f.readline()
                    continue
                v = eval(line)
                print(v)
                arr.append(' '.join([str(i) + '.', ':'.join([v['h'], v['p']])]))
                i+=1
                # arr.append(line)
                line = f.readline()
            f.close()

            # for i, v in enumerate(sessionJson, 1):
            #     arr.append(' '.join([str(i)+'.', ':'.join([v['h'], v['p']])]))
            write_result('\n'.join(arr))
            return
        try:
            list = int(list)
        except Exception as e:
            logger.exception(e)
            # TODO red error color
            print("(error)", str(e))
            return

        if isinstance(list, int):
            write_result('\n-------------'.join([str(sessionJson[list-1]), str(list-1)]))
            ctx.params['h'] = sessionJson[list-1]['h']
            ctx.params['p'] = sessionJson[list-1]['p']
#
# if __name__=='__main__':
#     print(sys.path)
#     file = os.path.expanduser('~')+'/session/host.json'
#     ctx = {}
#     ctx["params"] = {"ss":"l"}
#     arr = list(ctx=ctx)
#     write_result('\n'.join(arr))
#     ctx["params"] = {"ss": "6"}
#     getByIdx(ctx=ctx)
#     print(ctx)
#     # ctx["params"] = {"h":"192.168.88.155","p": "6380"}
#     # write(ctx)



