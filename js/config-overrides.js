//const path = require('path');

const entries = require('react-app-rewire-multiple-entry')([
    {
        entry: 'src/index.js',
    },
])

const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    webpack: function(config, env) {
        
        config.plugins=[
            new MiniCssExtractPlugin({
                filename: "aify.css",
            })
        ],
        config.output.library = 'aify';
        config.output.libraryExport = 'default';
        config.output.libraryTarget = 'umd';
        //config.output.path=path.join(__dirname, '../webui/static/aify/js'),
        //config.output.filename = 'aify-[chunkhash].js';
        config.output.filename = 'aify.js';
        //entries.addMultiEntry(config);
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