(function () {
  var fields = document.querySelectorAll('input[type="password"]');
  fields.forEach(function (input, i) {
    var id = 'fh-show-password-' + i;

    var wrap = document.createElement('div');
    wrap.className = 'fh-show-password';

    var box = document.createElement('input');
    box.type = 'checkbox';
    box.id = id;

    var label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = 'Show password';

    box.addEventListener('change', function () {
      input.type = box.checked ? 'text' : 'password';
    });

    wrap.appendChild(box);
    wrap.appendChild(label);
    input.insertAdjacentElement('afterend', wrap);
  });
})();