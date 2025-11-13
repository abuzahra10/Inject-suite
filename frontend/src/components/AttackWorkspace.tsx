import AttackGenerator from "./AttackGenerator";
import ChatConsole from "./ChatConsole";

export default function AttackWorkspace() {
  return (
    <div className="workspace-stack">
      <AttackGenerator />
      <ChatConsole />
    </div>
  );
}
