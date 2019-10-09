src = """
window.pywebview = {
    token: '%s',
    _rpc_id_prefix: Math.random().toString(36).substring(2,6)+'.',
    _rpc_id_sequence: 0,
    _createApi: function(funcList) {
        for (var i = 0; i < funcList.length; i++) {
            window.pywebview.api[funcList[i]] = (function (funcName) {
                return function() {
                    var rpc_id = window.pywebview._rpc_id_prefix+(
                        ++window.pywebview._rpc_id_sequence);
                    var rpc_request = {name:funcName, rpc_id:rpc_id, args:Array.from(arguments)}
                    window.pywebview._bridge.call(rpc_request);
                    return new Promise(function(resolve, reject) {
                        function on_rpc_settle(ev){
                            if (ev.detail.rpc_id == rpc_request.rpc_id){
                                window.removeEventListener('rpc_settle', on_rpc_settle);
                                if (ev.detail.success)
                                    resolve(ev.detail.value);
                                else
                                    reject(ev.detail.value);
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
                    return window.external.call(funcName, params);
                case 'edgehtml':
                    return window.external.notify(JSON.stringify([funcName, params]));
                case 'cocoa':
                    return window.webkit.messageHandlers.jsBridge.postMessage(
                        JSON.stringify(rpc_request));
                case 'qtwebengine':
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        channel.objects.external.call(funcName, params);
                    });
                    break;
            }
        }
    },
    _rpcSettle: function(rpc_id, success, value){
        window.dispatchEvent(
            new CustomEvent('rpc_settle', {detail:{rpc_id:rpc_id, success:success, value:value}} )
        );
    },
    platform: '%s',
    api: {},
}

window.pywebview._createApi(%s);
"""
