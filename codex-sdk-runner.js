#!/usr/bin/env node
/**
 * Codex SDK Runner - Programmatic control of Codex with streaming live logs
 * Usage: codex-sdk "your instruction"
 *        codex-sdk --write-enabled "your instruction"  # Write-enabled mode (allows file edits)
 *        codex-sdk --yolo "your instruction"  # YOLO mode (bypasses sandbox/approvals)
 * 
 * Uses @openai/codex-sdk for programmatic control with streaming
 * Reference: https://github.com/openai/codex/tree/main/sdk/typescript
 */

// Use dynamic import for ES module
async function main() {
  const args = process.argv.slice(2);
  let yoloMode = false;
  let writeEnabled = false;
  let prompt = "";
  
  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--yolo" || args[i] === "-y") {
      yoloMode = true;
    } else if (args[i] === "--write-enabled" || args[i] === "-w") {
      writeEnabled = true;
    } else {
      prompt += (prompt ? " " : "") + args[i];
    }
  }
  
  // Check for modes via environment variables
  if (process.env.CODEX_YOLO === "1" || process.env.CODEX_YOLO === "true") {
    yoloMode = true;
  }
  if (process.env.CODEX_WRITE_ENABLED === "1" || process.env.CODEX_WRITE_ENABLED === "true") {
    writeEnabled = true;
  }
  
  // Default to write-enabled if neither mode is explicitly set (for full loop workflows)
  if (!yoloMode && !writeEnabled) {
    writeEnabled = true;
  }
  
  if (!prompt) {
    console.error("Usage: codex-sdk [--write-enabled|--yolo] <prompt>");
    console.error("       codex-sdk <prompt>");
    console.error("");
    console.error("Options:");
    console.error("  --write-enabled, -w  Enable write access (allows file edits, rendering, etc.)");
    console.error("                       Default mode for full loop workflows");
    console.error("  --yolo, -y           Enable YOLO mode (full access, bypasses all safety)");
    console.error("                       WARNING: Only use in isolated environments (Docker/VM)!");
    console.error("");
    console.error("Environment variables:");
    console.error("  CODEX_WRITE_ENABLED=1  Enable write access (alternative to --write-enabled flag)");
    console.error("  CODEX_YOLO=1           Enable YOLO mode (alternative to --yolo flag)");
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
    const codexConfig = {
      apiKey: apiKey
    };
    
    // Configure sandbox and approval policy based on mode
    if (yoloMode) {
      // YOLO mode: full access, bypass all safety measures
      codexConfig.sandboxMode = "danger-full-access";
      codexConfig.approvalPolicy = "never";
    } else if (writeEnabled) {
      // Write-enabled mode: allows reading and writing within workspace
      codexConfig.sandboxMode = "workspace-write";
      codexConfig.approvalPolicy = "never";  // No prompts for automated workflows
    }
    // If neither mode is set, Codex defaults to read-only sandbox
    
    const codex = new Codex(codexConfig);
    const thread = codex.startThread();
    
    // Use streaming for live logs (suppress intermediate outputs)
    const streamedTurn = await thread.runStreamed(prompt);
    
    let finalResponse = null;
    let usage = null;
    let turnCompleted = false;
    
    // Process events silently, only capturing final response
    for await (const event of streamedTurn.events) {
      switch (event.type) {
        case "item.updated":
          // Only capture agent message text, don't display it yet
          if (event.item.type === "agent_message" && event.item.text) {
            finalResponse = event.item.text;
          }
          break;
          
        case "item.completed":
          if (event.item.type === "agent_message") {
            finalResponse = event.item.text;
          }
          break;
          
        case "turn.completed":
          turnCompleted = true;
          usage = event.usage;
          break;
          
        case "turn.failed":
          console.error("Error: Turn failed");
          if (event.error) {
            console.error(event.error.message || JSON.stringify(event.error));
          }
          process.exit(1);
          break;
          
        case "error":
          console.error(`Error: ${event.message || JSON.stringify(event)}`);
          break;
      }
    }
    
    // Show only the final response
    if (finalResponse) {
      console.log(finalResponse);
    } else if (!turnCompleted) {
      console.error("Error: No response received");
      process.exit(1);
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

