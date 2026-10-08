import { test, expect } from '@playwright/test';

test('operator can navigate a real governed decision from sample data to challenge and scenario', async ({ page }) => {
  const unexpectedErrors = [];
  page.on('pageerror', (error) => unexpectedErrors.push(error.message));
  await page.goto('/');
  await expect(page.getByText('Backend:')).toBeVisible();
  await expect(page.getByText('connected', { exact: true })).toBeVisible();

  await page.getByRole('button', { name: 'Load sample dataset' }).click();
  await expect(page.getByText('Sample industrial stream dataset loaded.')).toBeVisible();
  await page.getByRole('button', { name: 'Run recommendations' }).click();
  await expect(page.getByText('Rules engine, dashboard metrics and operational intelligence outputs refreshed.')).toBeVisible();

  await page.getByRole('tab', { name: 'Recommendations' }).click();
  await expect(page.getByRole('heading', { name: 'Circular recommendations' })).toBeVisible();
  await page.locator('.operator-list-row[title="Open S001"]').click();
  await page.getByRole('button', { name: 'Open review pack' }).click();
  await expect(page.getByRole('heading', { name: /S001: Aluminium machining offcuts/ })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Rule provenance' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Human review governance' })).toBeVisible();

  await page.locator('.governance-challenge-panel summary').click();
  const form = page.locator('.governance-challenge-panel form');
  await form.locator('input').nth(0).fill('CI Browser Test');
  await form.locator('input').nth(1).fill('Independent Waste Reviewer');
  await form.locator('textarea').nth(0).fill('Confirm alloy grade before closed-loop route acceptance.');
  await form.locator('textarea').nth(1).fill('A closed-loop screening route still requires specification evidence.');
  await form.getByRole('button', { name: 'Record challenge without overriding decision' }).click();
  await expect(page.getByText('Recorded For Governance Review', { exact: false })).toBeVisible();
  await expect(page.getByText('No Automatic Override', { exact: false })).toBeVisible();

  await page.getByRole('tab', { name: 'Scenario screening' }).click();
  await expect(page.getByRole('heading', { name: 'Intervention scenario screening' })).toBeVisible();
  await page.getByRole('button', { name: 'Run scenario', exact: true }).click();
  await expect(page.getByText('Scenario-screened recoverable quantity')).toBeVisible();
  await expect(page.getByText('Scenario screened for S001.')).toBeVisible();
  expect(unexpectedErrors).toEqual([]);
});

test('blind reviewer sees no answer until submitting all ten cases and analysis does not invent consensus', async ({ page }) => {
  const unexpectedErrors = [];
  page.on('pageerror', (error) => unexpectedErrors.push(error.message));
  await page.goto('/?mode=blind-review');
  await expect(page.getByRole('heading', { name: 'Blind circular-decision review' })).toBeVisible();
  await expect(page.getByText('0 / 10').first()).toBeVisible();
  await expect(page.getByText('System action revealed after submission')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Comparison unlocked' })).toHaveCount(0);

  const details = page.locator('.blind-reviewer-card');
  await details.getByPlaceholder('Reviewer name').fill('CI Browser Test Reviewer');
  await details.getByPlaceholder('e.g. Waste & Resource Manager').fill('Waste resource specialist');
  await details.locator('input[type=checkbox]').check();

  const submit = page.getByRole('button', { name: 'Submit and unlock comparison' });
  await expect(submit).toBeDisabled();
  for (let caseNumber = 1; caseNumber <= 10; caseNumber += 1) {
    const caseCard = page.locator('.blind-case-card');
    await expect(caseCard.getByText(`Case ${caseNumber} of 10`)).toBeVisible();
    const selects = caseCard.locator('.blind-question-grid select');
    await selects.nth(0).selectOption({ index: 1 });
    await selects.nth(1).selectOption('medium');
    await selects.nth(2).selectOption('true');
    await caseCard.locator('textarea').fill('Independent test judgement for UI regression, not professional validation.');
    if (caseNumber < 10) await caseCard.getByRole('button', { name: 'Next case' }).click();
  }
  await expect(submit).toBeEnabled();
  await expect(page.getByRole('heading', { name: 'Comparison unlocked' })).toHaveCount(0);
  await submit.click();
  await expect(page.getByRole('heading', { name: 'Comparison unlocked' })).toBeVisible();
  await expect(page.getByText('System action revealed after submission').first()).toBeVisible();

  await page.goto('/?mode=review-analysis');
  await expect(page.getByRole('heading', { name: 'Multi-reviewer agreement' })).toBeVisible();
  await expect(page.getByRole('heading', { name: /More reviewers are needed for inter-reviewer agreement/ })).toBeVisible();
  expect(unexpectedErrors).toEqual([]);
});
