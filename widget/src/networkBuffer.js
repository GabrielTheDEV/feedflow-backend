// networkBuffer.js
// Intercepta fetch e XHR, bufferiza últimas 50 falhas
const MAX_ENTRIES = 50;
let buffer = [];
let fetchWrapped = false;
let xhrWrapped = false;

function pushNetworkEntry(entry) {
  buffer.push(entry);
  if (buffer.length > MAX_ENTRIES) buffer.shift();
}

export function getNetworkBuffer() {
  return buffer.slice();
}

export function instrumentNetwork() {
  if (!fetchWrapped && window.fetch) {
    const origFetch = window.fetch;
    window.fetch = function(...args) {
      const start = Date.now();
      let method = 'GET', url = '';
      if (args[0]) {
        if (typeof args[0] === 'string') url = args[0];
        else if (args[0].url) url = args[0].url;
      }
      if (args[1] && args[1].method) method = args[1].method;
      return origFetch.apply(this, args).then(
        resp => {
          if (!resp.ok) {
            pushNetworkEntry({
              type: 'fetch', method, url, status: resp.status, duration: Date.now() - start, success: false, timestamp: Date.now()
            });
          }
          return resp;
        },
        err => {
          pushNetworkEntry({
            type: 'fetch', method, url, status: null, duration: Date.now() - start, success: false, error: String(err), timestamp: Date.now()
          });
          throw err;
        }
      );
    };
    fetchWrapped = true;
  }
  if (!xhrWrapped && window.XMLHttpRequest) {
    const OrigXHR = window.XMLHttpRequest;
    function XHRProxy() {
      const xhr = new OrigXHR();
      let url = '', method = '';
      let start = 0;
      xhr.open = function(m, u, ...rest) {
        method = m;
        url = u;
        start = Date.now();
        return OrigXHR.prototype.open.apply(xhr, [m, u, ...rest]);
      };
      xhr.addEventListener('loadend', function() {
        if (xhr.status >= 400) {
          pushNetworkEntry({
            type: 'xhr', method, url, status: xhr.status, duration: Date.now() - start, success: false, timestamp: Date.now()
          });
        }
      });
      xhr.addEventListener('error', function(e) {
        pushNetworkEntry({
          type: 'xhr', method, url, status: null, duration: Date.now() - start, success: false, error: 'network error', timestamp: Date.now()
        });
      });
      return xhr;
    }
    window.XMLHttpRequest = XHRProxy;
    xhrWrapped = true;
  }
}
