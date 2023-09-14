const input = document.getElementById("search-input");
const resultList = document.getElementById("user-boxes-container");

input.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    let filteredResult;

    if (query === "") {
        // When nothing is inputted, just print all users
        filteredResult = users;
    } else {
        filteredResult = users.filter((user) => {
            const concat_str = user.first_name + " " + user.last_name;
            return concat_str.toLowerCase().startsWith(query);
        });
    }

    resultList.innerHTML = "";

    filteredResult.forEach((user) => {
        // Create a new div element for each user
        const userBox = document.createElement("div");
        userBox.className = "user-box";
        userBox.style = "width:900px;height:50px;display:flex;justify-content: center;align-items:center;gap:20px;";
        userBox.innerHTML = `
            <span style="font-size: 15px;width:200px;">${user["first_name"]} ${user["last_name"]}</span>
            <span style="width:150px;">@${user["username"]}</span>
            <span style="width:80px;">${user["is_working"] ? "Active" : "Inactive"}</span>
            <span style="width:200px;">${user["email_address"]}</span>
        `;
        // Append the userBox to resultList
        resultList.appendChild(userBox);
    })
})