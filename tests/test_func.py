import func


def test_run(capsys):
    source = '''\
main = print (add1 x)
x = add1 40
add1 = add 1'''
    func.run(source)
    captured = capsys.readouterr()
    assert captured.out == '42\n'
