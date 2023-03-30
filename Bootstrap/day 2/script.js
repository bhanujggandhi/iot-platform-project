// function generateForm() {
//   $.getJSON("./config.json", function (data) {
//     let br = document.createElement("br");
//     let tab = document.createTextNode("\u00A0");
//     let form = document.createElement("form");
//     form.setAttribute("method", "get");
//     form.setAttribute("action", "");
//     document.getElementsByTagName("body")[0].appendChild(form);
//     Object.keys(data).forEach((key) => {
//       let label = document.createElement("label");
//       label.innerHTML = key;
//       let element = document.createElement("input");
//       element.setAttribute("name", key);
//       element.setAttribute("value", data[key]);
//       element.appendChild(label);
//       form.appendChild(label);
//       form.appendChild(tab.cloneNode());
//       form.appendChild(element);
//       form.appendChild(br.cloneNode());
//       element.addEventListener("input", function () {
//         data[key] = this.value;
//       });
//     });
//     let submitBtn = document.createElement("button");
//     let btnTag = document.createElement("label");
//     btnTag.innerHTML = "Submit";
//     submitBtn.appendChild(btnTag);
//     form.appendChild(submitBtn);
//     form.addEventListener("submit", function (e) {
//       e.preventDefault();
//       if (confirm("Are you sure you want to update the config file?")) {
//         console.log(JSON.stringify(data));
//         //     const filename = "myfile.txt";
//         //     window
//         //       .showSaveFilePicker()
//         //       .then(async (fileHandle) => {
//         //         const writable = await fileHandle.createWritable();
//         //         await writable.write(JSON.stringify(data));
//         //         await writable.close();
//         //         console.log("File saved successfully!");
//         //       })
//         //       .catch(console.error);
//       }
//     });
//   });
// }
// window.onload = generateForm;

function generateForm() {
  const form = document.createElement("form");
  form.setAttribute("method", "get");
  document.body.appendChild(form);

  fetch("./config.json")
    .then((response) => response.json())
    .then((data) => {
      Object.entries(data).forEach(([key, value]) => {
        const label = document.createElement("label");
        label.textContent = key;

        const input = document.createElement("input");
        input.setAttribute("name", key);
        input.setAttribute("value", value);
        input.addEventListener("input", () => {
          data[key] = input.value;
        });

        form.appendChild(label);
        form.appendChild(input);
        form.appendChild(document.createElement("br"));
      });

      const submitBtn = document.createElement("button");
      submitBtn.setAttribute("type", "submit");
      submitBtn.textContent = "Submit";
      form.appendChild(submitBtn);

      submitBtn.addEventListener("click", (event) => {
        event.preventDefault();
        const confirmMsg = "Are you sure you want to update the config file?";
        if (confirm(confirmMsg)) {
          const jsonData = JSON.stringify(data);
          console.log(jsonData);
          // send jsonData to server or save to file
        }
      });
    })
    .catch((error) => console.error(error));
}

window.addEventListener("load", generateForm);
