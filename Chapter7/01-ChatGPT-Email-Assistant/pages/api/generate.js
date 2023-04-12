import { Configuration, OpenAIApi } from "openai";

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

export default async function (req, res) {
  if (!configuration.apiKey) {
    res.status(500).json({
      error: {
        message: "OpenAI API 未設定，請按照 README.md 中的說明進行設置。",
      },
    });
    return;
  }

  const receiver = req.body.receiver || "";
  const content = req.body.content || "";
  const requirement = req.body.requirement || "";
  if (receiver.trim().length === 0) {
    res.status(400).json({
      error: {
        message: "請輸入收件人",
      },
    });
    return;
  }
  if (content.trim().length === 0) {
    res.status(400).json({
      error: {
        message: "請輸入內容",
      },
    });
    return;
  }

  try {
    const completion = await openai.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content:
            "你現在扮演一名專業的 Email 撰寫專家，我會提供給你收件者、信件內容以及信件書寫的需求，你需要依照提供的收件者、信件內容以及需求，撰寫一封完整且通順的信件。信件最後的部分，請用 Best Regards, /n[你的名字]。",
        },
        {
          role: "user",
          content: generatePrompt(receiver, content, requirement),
        },
      ],
    });
    res.status(200).json({ result: completion.data.choices[0].message });
  } catch (error) {
    // Consider adjusting the error handling logic for your use case
    if (error.response) {
      console.error(error.response.status, error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      console.error(`OpenAI API 請求發生錯誤：${error.message}`);
      res.status(500).json({
        error: {
          message: "伺服器發生錯誤",
        },
      });
    }
  }
}

const generatePrompt = (receiver, content, requirement) => {
  return `收件者：${receiver}
信件內容：${content}  
信件書寫需求：${requirement || "無"}
`;
};
