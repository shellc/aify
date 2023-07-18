//const path = require('path');

const entries = require('react-app-rewire-multiple-entry')([
    {
        entry: 'src/aify.js',
    },
])

module.exports = {
    webpack: function(config, env) {
        
        config.output.library = 'aify';
        config.output.libraryExport = 'default';
        config.output.libraryTarget = 'umd';
        config.output.filename = 'aify-[chunkhash].js';
        
        entries.addMultiEntry(config);
        return config;
    },
    
    devServer: function (configFunction) {
        return function(proxy, allowedHost) {
            const config = configFunction(proxy, allowedHost);
            //https://github.com/chimurai/http-proxy-middleware/issues/371
            config.compress = false;
            return config;
        }
    }
}