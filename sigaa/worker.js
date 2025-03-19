const { workerData, parentPort } = require("node:worker_threads");
const fs = require("node:fs/promises");
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function extractSubjectInfo(data) {
  const { window } = new JSDOM(data, { runScripts: "outside-only" });
  // pega a tabela que representa a relação de professores do período
  const materias = Array.from(
    window.document
      .querySelector("table#lista-turmas")
      .querySelectorAll("tbody tr"),
  ).filter((el) => el.style.display != "none");

  let result = [];
  let tmp = { materia: "", professores: [], periodo: "" };
  // itera sobre a lista
  for (let i = 0; i < materias.length; i++) {
    // trimmedValue remove \t e \n do começo do texto
    const trimmedValue = materias[i].textContent
      .replace("/^(\t|\n)+/", "")
      .trim();
    // splitted separa em newlines e remove \t e \n
    const splitted = trimmedValue
      .split("\n")
      .map((value) => value.replace("/^(\t|\n)+/", "").trim());

    // checa se o elemento é o nome do curso, que é diferente do resto das informações
    if (materias[i].classList.contains("destaque")) {
      const parenIndicator = splitted[0].indexOf("(", 6);
      tmp.materia = splitted[0].slice(8, parenIndicator - 1);
      continue;
    } else if (
      i != materias.length - 1 &&
      !materias[i + 1].classList.contains("destaque") // verifica se o uma matéria tem dois professores
    ) {
      const teacherName = splitted[7].slice(0, splitted[7].indexOf("(") - 1);
      tmp.professores.push(teacherName);
      continue;
    } else {
      const teacherName = splitted[7].slice(0, splitted[7].indexOf("(") - 1);
      tmp.professores.push(teacherName);
    }

    // adiciona o periodo
    tmp.periodo = splitted[0];
    result.push(tmp);
    tmp = { materia: "", professores: [], periodo: "" };
  }

  return result;
}

async function processFile(filePath) {
  try {
    const file = await fs.readFile(filePath, { encoding: "utf8" });
    const data = extractSubjectInfo(file);
    return data;
  } catch (err) {
    throw new Error(`Error processing ${filePath}: ${err.message}`);
  }
}

processFile(workerData)
  .then((result) => parentPort.postMessage(result)) // Send result to main thread
  .catch((err) => parentPort.postMessage({ error: err.message }));
