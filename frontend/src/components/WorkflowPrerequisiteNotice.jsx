export default function WorkflowPrerequisiteNotice({
  title = 'Run recommendations first',
  message = 'This workflow needs loaded data and locked rules-engine recommendations before it can be used.',
  actions = [],
}) {
  return (
    <section className="workflow-prerequisite-notice">
      <span className="eyebrow">Workflow guardrail</span>
      <h3>{title}</h3>
      <p>{message}</p>
      {!!actions.length && (
        <ul>
          {actions.map((action, index) => (
            <li key={`workflow-action-${index}`}>{action}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
