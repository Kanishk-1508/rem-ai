import FileUpload from "./FileUpload";
import Chat from "./Chat";
import "./App.css";

function App() {
  return (
    <div className="app">
      <h1 className="title">rem.ai</h1>
      <p className="subtitle">
        Ask questions based on your uploaded documents
      </p>

      <FileUpload />
      <Chat />
    </div>
  );
}

export default App;
