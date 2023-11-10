function manager_select_handler(event, outputContainerElement, hiddenManagerIdStorer){

    // todo: ensure that if clicked on places that's not on span, it still works


    if (!(event.target.tagName.toLowerCase() === 'span')){
        return;
    }

    // if a manager is selected
    const manager = event.target.parentNode;
    if (manager.classList.contains("selected-manager")){
       manager.classList.remove("selected-manager");
       hiddenManagerIdStorer.value = null;
    }else{
        // delete all other users in the manager candidates container
        outputContainerElement.innerHTML = "";
        manager.classList.add("selected-manager");
        outputContainerElement.appendChild(manager);
        hiddenManagerIdStorer.value = manager.dataset.id;
    }

}