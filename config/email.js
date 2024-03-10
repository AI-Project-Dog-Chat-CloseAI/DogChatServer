module.exports = {
    host: process.env.HOST || "smtp.gmail.com",
    post: process.env.POST || 587,
    secure: false,
    auth: {
        user: process.env.USER || "yukipham0702@gmail.com",
        pass: process.env.PASS || "ogwn sato wznz sukr",
    }
}