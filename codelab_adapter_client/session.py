'''
Session object for building, serializing, sending, and receiving messages.
The Session object supports serialization, HMAC signatures,
and metadata on messages.

Also defined here are utilities for working with Sessions:
* A Message object for convenience that allows attribute-access to the msg dict.

ref: https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/session.py
'''
import pprint
import os
from datetime import datetime
from datetime import timezone
utc = timezone.utc

from ._version import protocol_version


class Message:
    """A simple message object that maps dict keys to attributes.
    A Message can be created from a dict and a dict from a Message instance
    simply by calling dict(msg_obj)."""

    def __init__(self, msg_dict):
        dct = self.__dict__
        for k, v in (dict(msg_dict)).items():
            if isinstance(v, dict):
                v = Message(v)
            dct[k] = v

    # Having this iterator lets dict(msg_obj) work out of the box.
    def __iter__(self):
        return iter((self.__dict__).items())

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def __contains__(self, k):
        return k in self.__dict__

    def __getitem__(self, k):
        return self.__dict__[k]


def utcnow():
    """Return timezone-aware UTC timestamp"""
    return datetime.utcnow().replace(tzinfo=utc)


def msg_header(msg_id, msg_type, username, session):
    """Create a new message header

    'header' : {
        'msg_id' : str, # typically UUID, must be unique per message
        'session' : str, # typically UUID, should be unique per session
        'username' : str, # Username for the Session. Default is your system username.
        # ISO 8601 timestamp for when the message is created
        'date': str,
        # All recognized message type strings are listed below.
        'msg_type' : str, # 枚举
        # the message protocol version
        'version' : '3.0',
        },
    """
    date = utcnow()
    version = protocol_version
    return locals()


def extract_header(msg_or_header):
    """Given a message or header, return the header."""
    if not msg_or_header:
        return {}
    try:
        # See if msg_or_header is the entire message.
        h = msg_or_header['header']
    except KeyError:
        try:
            # See if msg_or_header is just the header
            h = msg_or_header['msg_id']
        except KeyError:
            raise
        else:
            h = msg_or_header
    if not isinstance(h, dict):
        h = dict(h)
    return h

def msg(self, msg_type, content=None, parent=None, header=None, metadata=None):
        """Return the nested message dict.
        This format is different from what is sent over the wire. The
        serialize/deserialize methods converts this nested message dict to the wire
        format, which is a list of message parts.

        'header':{}
        'msg_id' : str, #uuid
        'msg_type' : str, # _reply消息必须具有parent_header
        'parent_header' : dict,
        'content' : dict,
        'metadata' : {}, # 不常使用
        """
        msg = {}
        header = self.msg_header(msg_type) if header is None else header
        msg['header'] = header
        msg['msg_id'] = header['msg_id']
        msg['msg_type'] = header['msg_type']
        msg['parent_header'] = {} if parent is None else extract_header(parent)
        msg['content'] = {} if content is None else content
        msg['metadata'] = metadata
        # buffer
        return msg

def sign(self, msg_list):
        """
        https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/session.py#L592

        Sign a message with HMAC digest. If no auth, return b''.
        Parameters
        ----------
        msg_list : list
            The [p_header,p_parent,p_content] part of the message list.
        """
        pass


username = os.environ.get('USER', 'username') , # 3.0, Username for the Session. Default is your system username.


def _message_template(sender,node_id,token):
    '''
        topic: self.TOPIC: channel
        payload:
            node_id? //类似jupyter kernel
            content
            sender 类似 session_id 进程名字
            timestamp? date

            msg['msg_id'] = header['msg_id']
            msg['msg_type'] = header['msg_type']
            msg['parent_header'] // 触发的消息
            'username' : str, # Username for the Session. Default is your system username.
    '''
    template = {
            "payload": {
                "parent_header": {}, # 3.0, reply
                "version": protocol_version,  # 3.0
                "content": "content", # string or dict
                "sender": sender,  # like session (uuid)， adapter/nodes/<classname>
                "username": username , # 3.0, Username for the Session. Default is your system username.
                "node_id": node_id, # like jupyter kernel id/name
                "message_id": "", # session + count # uuid
                "message_type": "", # 3.0 deside content reply/req/pub
                "token": token
            }
        }
    return template