const nodemailer = require('nodemailer');
const config = require('config');

module.exports = async (html, mail) => {
    await nodemailer.createTransport(config.get("email")).sendMail({
        to: mail,
        from: '"CloseAI Company" <yukipham0702@gmail.com>',
        subject: "Verify account",
        html
    })
}