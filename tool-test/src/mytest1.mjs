import 'dotenv/config';
import { ChatOpenAI } from '@langchain/openai';

const model = new ChatOpenAI({
    modelName: process.env.MODEL_NAME || 'qwen-coder-turbo',
    apiKey: process.env.OPENAI_API_KEY,
    configuration: {
        baseURL: process.env.OPENAI_BASE_URL,
    },
});

const response = await model.invoke('你好呀哇咔咔');
console.log(response.content);