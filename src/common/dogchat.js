const axios = require('axios');

module.exports = async (message) => {
    try {
        const response = await axios.post('http://127.0.0.1:5000', {
            question : message
        });
        return response.data;
    } catch (err) {
        return "Xin lỗi tôi không thể trả lời câu hỏi này của bạn"
    }
}

