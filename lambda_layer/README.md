# creating aws lambda layers for python and third party libraries

This example lambda layer uses the [Paramiko SSH library](https://www.paramiko.org/).

## python versions
* `Python 3.9`: use Fedora 34
* `Python 3.10`: use Fedora 35

## example
```bash
pip3 install -t third_party paramiko
zip -9r paramiko-py39.zip paramiko
```

## lambda usage
```python
import sys
sys.path.append("/opt/third_party")

try:
    import paramiko
except ModuleNotFoundError as err:
    print(f"{err}")
    sys.exit()

client = paramiko.SSHClient()
print(client)
```
