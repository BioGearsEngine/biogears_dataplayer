module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "/showcase/" : "/",
  indexPath: "showcase.html",
  pluginOptions: {
    electronBuilder: {
      nodeIntegration: true,
      builderOptions: {
        productName: "BioGears Showcase Player"
      }
    }
  }
}
