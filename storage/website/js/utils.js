function getRadioGroupValue(selector) {
    const radios = document.querySelectorAll(selector);
    let selectedValue;
    radios.forEach(radio => {
        if (radio.checked) selectedValue = radio.value;
    });
    return selectedValue;
}