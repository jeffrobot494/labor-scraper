# Claude Working Instructions

## Working Process

### Definition of a "Task"
- Any request for code changes, no matter how small or whether it's a "fix" 
- Any follow-up adjustments to previous work, including bug fixes
- Any implementation of features, even if they seem straightforward
- ANY change to ANY file, regardless of perceived complexity

### Planning-First Workflow (MANDATORY)
1. **NEVER implement without prior approval**
2. For ANY task (coding, file creation, architecture design, fixes, adjustments):
   - First outline your complete approach
   - List files to be modified with line numbers where possible
   - Show example structures/code snippets
   - Highlight key decisions that need to be made
3. **Wait for EXPLICIT approval before implementing ANY changes**
   - Do not assume approval is implicit
   - Do not implement "obvious" fixes without approval
   - If the user asks for changes to previous work, treat it as a new task
4. After implementation, summarize what was done
5. If in doubt about scope, ask for clarification first

### Technical Approach
- Fix issues by understanding root causes, not through speculative changes
- Validate assumptions before implementing solutions

### Debugging Process
- Diagnose issues systematically, not through trial and error
- Consider what the user might be doing/seeing when experiencing issues
- Use clear logging to expose important state information
- Question whether framework/engine assumptions are correct

### Implementation Philosophy
- Consider the unique requirements of TCG World, namely that it is a game creation platform rather than a game itself, when deciding how to implement systems and solutions
- Make the data layer match users' mental model (e.g., rotation values)
- Keep separations clean between data definition and implementation details
- Create self-documenting code with clear comments about design decisions

### Workflow Examples
#### Example 1: Initial Task
User: "Create a function to fetch game data"
Claude: [Provides plan with files to modify and code samples]
User: "Proceed with the changes"
Claude: [Implements changes and summarizes]

#### Example 2: Follow-up Fix
User: "The function isn't fetching the correct field"
Claude: [Provides a NEW PLAN with files to modify and code samples]
User: "Proceed"
Claude: [Implements changes and summarizes]

#### Example 3: Small Adjustment (still requires planning)
User: "Change the font size to 14px"
Claude: [Provides plan showing the CSS to change]
User: "Proceed"
Claude: [Implements changes and summarizes]

### Process Failure Recovery
If you realize you've made changes without following the proper planning-first workflow:
1. Acknowledge the process error immediately
2. Explain what you did and why it was incorrect
3. Propose a plan for any additional changes needed
4. Wait for explicit approval before making ANY further changes
5. After approval, implement only the approved changes

## Engineering Principles

1. **Simplicity First** - Always prefer simple, understandable solutions over complex ones
2. **Work With The System** - Leverage Unity's built-in capabilities rather than fighting against them
3. **Single Source of Truth** - Centralize configuration and avoid duplicating logic
4. **Prefer Composition Over Inheritance** - Design systems assembled from smaller components
5. **Minimize State Complexity** - Keep state management simple and predictable
6. **Standard Before Custom** - Use standard approaches before creating custom solutions
7. **Test Edge Cases Early** - Identify and test boundary conditions from the start
8. **Refactor Toward Simplicity** - Make code simpler when improving it
9. **Clear Ownership** - Each functionality should have one clear "owner" component
10. **Pragmatic Approach** - Favor working solutions that solve immediate problems clearly

## Project-Specific Guidelines

- Focus on minimal working implementations first
- Prioritize correct rendering and positioning of cards
- Follow the simplified architecture in tcg-architecture.md
- Create clear separation between data, logic, and presentation layers