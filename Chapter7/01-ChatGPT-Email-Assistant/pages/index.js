import Head from "next/head";
import { useState } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [receiverValue, setReceiverValue] = useState("");
  const [contentValue, setContentValue] = useState("");
  const [requirementValue, setRequirementValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState();

  async function onSubmit(event) {
    setLoading(true);
    event.preventDefault();
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          receiver: receiverValue,
          content: contentValue,
          requirement: requirementValue,
        }),
      });

      const data = await response.json();
      if (response.status !== 200) {
        throw (
          data.error || new Error(`請求發生錯誤，因為： ${response.status}`)
        );
      }

      setResult(data.result.content);
      setReceiverValue("");
      setContentValue("");
      setRequirementValue("");
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Head>
        <title>Email 產生器</title>
        <link rel="icon" href="/logo.png" />
      </Head>

      <main className={styles.main}>
        <img src="/logo.png" className={styles.icon} />
        <h3>Email 產生器</h3>
        <form onSubmit={onSubmit}>
          <label for="receiver">收件者</label>
          <input
            type="text"
            id="receiver"
            name="receiver"
            placeholder="例如：張經理"
            value={receiverValue}
            onChange={(e) => setReceiverValue(e.target.value)}
          />
          <label for="content">這封 Email 要做什麼？</label>
          <textarea
            id="content"
            name="content"
            rows={5}
            placeholder="例如：想要與 ABC 公司討論合作事項"
            value={contentValue}
            onChange={(e) => setContentValue(e.target.value)}
          />
          <label for="requirement">是否有其他需求？(如無，則可不填)</label>
          <textarea
            id="requirement"
            name="requirement"
            rows={5}
            placeholder="例如：信件的語氣要輕鬆"
            value={requirementValue}
            onChange={(e) => setRequirementValue(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? <LoadingSpinner /> : "Email 生成"}
          </button>
        </form>
        <div className={styles.result}>{result}</div>
      </main>
    </div>
  );
}

const LoadingSpinner = () => {
  return <span className={styles.loader}></span>;
};
