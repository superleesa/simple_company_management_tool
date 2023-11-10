function findUser(inputElement, outputContainerElement, users, show_all_users_by_default=true){
    const query = inputElement.value.toLowerCase();
    let filteredResult;

    if (query === "") {
        // When nothing is inputted, just print all users
        filteredResult = show_all_users_by_default ? users : [];
    } else {
        filteredResult = users.filter((user) => {
            const concat_str = user.first_name + " " + user.last_name;
            return concat_str.toLowerCase().startsWith(query);
        });
    }

    outputContainerElement.innerHTML = "";

    filteredResult.forEach((user) => {
        // Create a new div element for each user
        const userBox = document.createElement("div");
        userBox.dataset.id = user["id"];
        userBox.className = "user-box";
        // userBox.style = "width:900px;height:50px;display:flex;justify-content: center;align-items:center;gap:20px;";
        userBox.innerHTML = `
            <span class="full-name-span">${user["first_name"]} ${user["last_name"]}</span>
            <span class="username-span">@${user["username"]}</span>
            <span class="is-working-span">${user["is_working"] ? "Active" : "Inactive"}</span>
            <span class="email-address-span">${user["email_address"]}</span>
        `;
        // Append the userBox to resultList
        outputContainerElement.appendChild(userBox);
    })
}