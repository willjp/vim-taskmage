from taskmage2.testutils import core

# =====
# Nodes
# =====

def node_task(_id=None, name=None, data=None, children=None):
    if _id is None:
        _id = core.uuid
    if name is None:
        name = core.defaulttask['name']
    if data is None:
        data = core.defaulttask['data'].copy()

    return data.Node(_id=_id, ntype='task', name=name, data=data, children=children)


def node_section(_id=None, name=None, data=None, children=None):
    if _id is None:
        _id = core.uuid
    if name is None:
        name = core.defaultsection['name']
    if data is None:
        data = core.defaultsection['data'].copy()

    return data.Node(_id=_id, ntype='section', name=name, data=data, children=children)


def node_file(_id=None, name=None, data=None, children=None):
    if _id is None:
        _id = core.uuid
    if name is None:
        name = core.defaultfile['name']
    if data is None:
        data = core.defaultfile['data'].copy()

    return data.Node(_id=_id, ntype='file', name=name, data=data, children=children)
