async function sendMessage() {

    try {

        let input = document.getElementById("userInput");
        let chatArea = document.getElementById("chatArea");

        let userText = input.value;

        if(userText === ""){
            return;
        }

        chatArea.innerHTML += `
            <div class="user-message">
                ${userText}
            </div>
        `;

        console.log("Sending:", userText);

        const response = await fetch(
    "https://hr-rag-chatbot.onrender.com/chat",
{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userText
            })
        });

        console.log("Response:", response);

        const data = await response.json();


        console.log("Data:", data);

        chatArea.innerHTML += `
            <div class="bot-message">
                ${data.reply}
            </div>
        `;

        input.value = "";

    }
    catch(error){

        console.error("ERROR:", error);

        alert(error);

    }
}