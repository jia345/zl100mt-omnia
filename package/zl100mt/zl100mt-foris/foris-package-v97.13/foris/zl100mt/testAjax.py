from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.Routing import cmdRoutingInfor
from foris.zl100mt.portmapping import channelmapping,setportmapping
import bottle


def ts_ipmacbind(session):
    data = {}
    cmdIpmacbind.implement(data, session)

def ts_route(session):
    data = {"action": "route"}
    cmdRoutingInfor.implement(data, session)
    # cmdRoutingInfor.get_routes(data)

def ts_channelmap(session):
    res = channelmapping.get_slotLTEZ()
    print res

def ts_portmap(session):
    res = setportmapping.get_portmapping()

test_app = {
    'ip2mac': ts_ipmacbind,
    'route' : ts_route,
    'channel': ts_channelmap,
    'portmap': ts_portmap,
}

def run_ajax_test():
    if bottle.request.method == 'POST':
        pass
    else :
        action = bottle.request.GET.get('action')
        print "run_ajax_test:",action
    session = bottle.request.environ['foris.session']
    test_app[action](session)


