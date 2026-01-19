#!/usr/bin/env node
/**
 * Codex SDK Runner - Programmatic control of Codex with streaming live logs
 * Usage: codex-sdk "your instruction"
 * 
 * Uses @openai/codex-sdk for programmatic control with streaming
 * Reference: https://github.com/openai/codex/tree/main/sdk/typescript
 */

// Use dynamic import for ES module
async function main() {
  const prompt = process.argv.slice(2).join(" ");
  
  if (!prompt) {
    console.error("Usage: codex-sdk <prompt>");
    process.exit(1);
  }

  try {
    // Check for API key
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      console.error("Error: OPENAI_API_KEY environment variable is required");
      process.exit(1);
    }

    // Dynamic import for ES module - try local install first, then global
    let Codex;
    try {
      const sdk = await import("/usr/local/lib/codex-sdk-runner/node_modules/@openai/codex-sdk/dist/index.js");
      Codex = sdk.Codex;
    } catch (e) {
      // Fallback to global install
      const sdk = await import("@openai/codex-sdk");
      Codex = sdk.Codex;
    }
    
    // Initialize Codex with API key from environment variable
    const codex = new Codex({
      apiKey: apiKey
    });
    const thread = codex.startThread();
    
    console.log(`Running Codex with prompt: "${prompt}"`);
    console.log("---\n");
    
    // Use streaming for live logs
    const streamedTurn = await thread.runStreamed(prompt);
    
    let finalResponse = null;
    let usage = null;
    let turnCompleted = false;
    const commandOutputs = new Map(); // Track what we've shown to avoid duplicates
    
    // Process events as they stream in
    for await (const event of streamedTurn.events) {
      switch (event.type) {
        case "thread.started":
          console.log(`[Thread started: ${event.thread_id}]\n`);
          break;
          
        case "turn.started":
          console.log("[Turn started]\n");
          break;
          
        case "item.started":
          if (event.item.type === "agent_message") {
            console.log("\n[Agent message]");
          } else if (event.item.type === "command_execution") {
            console.log(`\n[Command] ${event.item.command}`);
            commandOutputs.set(event.item.id, "");
          } else if (event.item.type === "file_change") {
            const changes = event.item.changes.map(c => `${c.kind}: ${c.path}`).join(", ");
            console.log(`\n[File changes] ${changes}`);
          } else if (event.item.type === "reasoning") {
            console.log("\n[Reasoning]");
          } else if (event.item.type === "web_search") {
            console.log(`\n[Web search] ${event.item.query}`);
          }
          break;
          
        case "item.updated":
          if (event.item.type === "command_execution") {
            // Show command output incrementally as it streams
            if (event.item.aggregated_output) {
              const lastOutput = commandOutputs.get(event.item.id) || "";
              const currentOutput = event.item.aggregated_output;
              // Only show new output (difference) to avoid duplicates
              if (currentOutput.length > lastOutput.length) {
                const newOutput = currentOutput.slice(lastOutput.length);
                process.stdout.write(newOutput);
                commandOutputs.set(event.item.id, currentOutput);
              } else if (currentOutput && !lastOutput) {
                // First time seeing output for this command
                process.stdout.write(currentOutput);
                commandOutputs.set(event.item.id, currentOutput);
              }
            }
          } else if (event.item.type === "agent_message") {
            // Stream agent message text as it's generated
            if (event.item.text) {
              process.stdout.write(event.item.text);
            }
          } else if (event.item.type === "reasoning") {
            // Stream reasoning text
            if (event.item.text) {
              process.stdout.write(event.item.text);
            }
          }
          break;
          
        case "item.completed":
          if (event.item.type === "agent_message") {
            // Ensure newline after agent message
            console.log("\n");
            finalResponse = event.item.text;
          } else if (event.item.type === "command_execution") {
            // Show command output when command completes
            const cmdItem = event.item;
            const shownOutput = commandOutputs.get(cmdItem.id) || "";
            
            if (cmdItem.aggregated_output) {
              const fullOutput = cmdItem.aggregated_output;
              // Only show if we haven't shown it all already
              if (fullOutput.length > shownOutput.length) {
                const newOutput = fullOutput.slice(shownOutput.length);
                if (newOutput.trim()) {
                  console.log(newOutput.trim());
                }
                commandOutputs.set(cmdItem.id, fullOutput);
              } else if (fullOutput && !shownOutput) {
                // First time seeing output - show it all
                const trimmed = fullOutput.trim();
                if (trimmed) {
                  console.log(trimmed);
                  commandOutputs.set(cmdItem.id, fullOutput);
                }
              }
            }
            
            if (cmdItem.exit_code !== undefined && cmdItem.exit_code !== 0) {
              console.log(`[Exit code: ${cmdItem.exit_code}]`);
            }
            
            // Don't delete - keep for potential future updates
          } else if (event.item.type === "file_change") {
            const status = event.item.status === "completed" ? "✓" : "✗";
            console.log(`[File changes ${status}]`);
          }
          break;
          
        case "turn.completed":
          turnCompleted = true;
          usage = event.usage;
          // Show final response if we have it
          if (finalResponse) {
            console.log("\n---\n[Final Response]");
            console.log(finalResponse);
          }
          console.log("\n---\n[Turn completed]");
          break;
          
        case "turn.failed":
          console.error("\n---\n[Turn failed]");
          if (event.error) {
            console.error(`Error: ${event.error.message || JSON.stringify(event.error)}`);
          }
          process.exit(1);
          break;
          
        case "error":
          console.error(`\n[Error] ${event.message || JSON.stringify(event)}`);
          break;
      }
    }
    
    // Show final response if not already displayed
    if (finalResponse && !turnCompleted) {
      console.log("\n---\n[Final Response]");
      console.log(finalResponse);
    }
    
    // Show usage if available
    if (usage) {
      console.log("\n--- Usage ---");
      console.log(`Input tokens: ${usage.input_tokens || 0}`);
      console.log(`Output tokens: ${usage.output_tokens || 0}`);
    }
    
    process.exit(0);
  } catch (error) {
    console.error("Error running Codex SDK:", error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

main();

