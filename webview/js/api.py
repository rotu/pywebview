src = """
window.pywebview = {
    token: '%s',
    _rpc_id_sequence: Math.floor(Math.random()*(2**32)),
    _createApi: function(funcList) {
        for (var i = 0; i < funcList.length; i++) {
            window.pywebview.api[funcList[i]] = (function (funcName) {
                return function() {
                    var rpc_request = {
                        rpc_id:++window.pywebview._rpc_id_sequence,
                        name:funcName,
                        args:Array.from(arguments)
                    }
                    window.pywebview._bridge.call(rpc_request);
                    return new Promise(function(resolve, reject) {
                        function on_rpc_settle(ev){
                            if (ev.detail.rpc_id == rpc_request.rpc_id){
                                window.removeEventListener('rpc_settle', on_rpc_settle);
                                if (ev.detail.error)
                                    reject(ev.detail.error)
                                else
                                    resolve(ev.detail.value);
                            }
                        }
                        window.addEventListener('rpc_settle', on_rpc_settle); 
                    });
                }
            })(funcList[i])
        }
    },
    _bridge: {
        call: function (rpc_request) {
            switch(window.pywebview.platform) {
                case 'mshtml':
                case 'cef':
                case 'qtwebkit':
                    return window.external.call(JSON.stringify(rpc_request));
                case 'edgehtml':
                    return window.external.notify(JSON.stringify(rpc_request));
                case 'cocoa':
                    return window.webkit.messageHandlers.jsBridge.postMessage(
                        JSON.stringify(rpc_request));
                case 'qtwebengine':
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        channel.objects.external.call(JSON.stringify(rpc_request));
                    });
                    break;
            }
        }
    },
    _rpcSettle: function(rpc_response){
        window.dispatchEvent(
            new CustomEvent('rpc_settle', {detail:rpc_response} )
        );
    },
    platform: '%s',
    api: {},
}

window.pywebview._createApi(%s);
"""
