module.exports = {
    port : process.env.SERVER_PORT || 7200,
    view_folder : `${__dirname}/../src/apps/views`,
    view_engine : "ejs",
    key : process.env.KEY,
    client_domain : process.env.DOMAIN
}