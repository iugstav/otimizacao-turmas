const fs = require("node:fs");
const path = require("node:path");
const { Worker, workerData } = require("node:worker_threads");
const { createObjectCsvWriter } = require("csv-writer");

const files = fs.readdirSync("./turmas").map((val) => "./turmas/" + val);

async function handleWorkers(filepaths, output) {
  const writer = createObjectCsvWriter({
    path: output,
    header: [
      { id: "materia", title: "Matéria" },
      { id: "professores", title: "Professores" },
      { id: "periodo", title: "Período" },
    ],
  });

  const workers = filepaths.map((fp) => {
    return new Promise((resolve, reject) => {
      const worker = new Worker("./worker.js", {
        workerData: fp,
      });

      worker.on("message", resolve);
      worker.on("error", reject);
      worker.on("exit", (code) => {
        if (code != 0)
          reject(new Error(`Worker stopped with exit code ${code}`));
      });
    });
  });

  try {
    const result = await Promise.all(workers);
    await writer.writeRecords(result.flat());
    console.info("successfully written to csv");
  } catch (err) {
    console.error("error processing files: ", err);
  }
}

const dataDir = path.join(__dirname, "..", "data");
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir);
handleWorkers(files, path.join(dataDir, "output.csv"));
