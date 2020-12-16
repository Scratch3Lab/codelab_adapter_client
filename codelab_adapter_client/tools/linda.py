'''
codelab-linda --monitor
codelab-linda --out [1, "hello"]
codelab-linda --rd [1, "*"]
codelab-linda --in [1, "hello"]
codelab-linda --dump

list 解析，json 输出，彩色
子命令

click, adapter full 已经内置 click
'''
import time
import click
import ast
from codelab_adapter_client import AdapterNode


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)


class CatchAllExceptions(click.Group):
    # https://stackoverflow.com/questions/44344940/python-click-subcommand-unified-error-handling
    def __call__(self, *args, **kwargs):
        try:
            return self.main(standalone_mode=False, *args, **kwargs)
        except Exception as e:
            click.echo(e)
        finally:
            mynode.terminate()  # ok!


class MyNode(AdapterNode):
    NODE_ID = "eim/cli_linda_client"

    def __init__(self):
        super().__init__()


mynode = MyNode()
mynode.receive_loop_as_thread()
time.sleep(0.05)


@click.group(cls=CatchAllExceptions)
@click.option('-i',
              '--ip',
              envvar='IP',
              help="IP Address of Adapter",
              default="127.0.0.1",
              required=False)
@click.pass_context
def cli(ctx, ip):
    '''
    talk with linda from cli
    '''
    # ctx.obj = mynode # todo ip ，多参数
    ctx.ensure_object(dict)
    ctx.obj['node'] = mynode
    ctx.obj['ip'] = ip


@click.command()
@click.pass_obj
def dump(ctx):
    '''
    dump all tuples from Linda tuple space
    '''
    res = ctx['node'].linda_dump()
    click.echo(res)
    return ctx['node']


@cli.command()
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def out(ctx, data):
    '''
    out the tuple to Linda tuple space
    '''
    # codelab-linda out --data '[1, "hello"]'
    # codelab-linda --ip '192.168.31.111'  out --data '[1, "hello"]' # 注意参数位置！
    assert isinstance(data, list)
    click.echo(f'ip: {ctx["ip"]}')
    res = ctx['node'].linda_out(data)
    click.echo(res)
    return ctx['node']


@click.command("in")
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def in_(ctx, data):  # replace
    '''
    in the tuple to Linda tuple space
    '''
    # codelab-linda in --data '[1, "*"]'

    assert isinstance(data, list)
    res = ctx["node"].linda_in(data)
    click.echo(res)
    return ctx["node"]


@click.command("inp")
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def inp(ctx, data):  # replace
    '''
    inp(in but Non-blocking) the tuple to Linda tuple space
    '''
    # codelab-linda in --data '[1, "*"]'

    assert isinstance(data, list)
    res = ctx["node"].linda_inp(data)
    click.echo(res)
    return ctx["node"]


@cli.resultcallback()
def process_result(result, **kwargs):
    # click.echo(f'After command: {result} {kwargs}')
    # result is node
    if result._running:
        result.terminate()


'''
if __name__ == '__main__':
    cli(obj={})

'''

cli.add_command(dump)
cli.add_command(out)
cli.add_command(in_)
cli.add_command(inp)

# 不阻塞一直跑