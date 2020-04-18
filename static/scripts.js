function validatePassLength(input) {
  if (input.value.length < 6) {
    input.setCustomValidity("Your password should be at least 6 symbols long.");
  }
  else {
    input.setCustomValidity("");
  }
}

function validatePasses(input2) {
  var input1 = document.getElementById("input-password1");
  if (input1.value !== input2.value) {
    input2.setCustomValidity("Passwords mismatch.");
  }
  else {
    input2.setCustomValidity("");
  }
}
