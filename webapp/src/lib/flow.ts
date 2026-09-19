/**
 * Port of modules/track1/07_prisma_flow_tracker/flow_tracker.py.
 *
 * Same fields, same derived counts, same conservation check (every
 * stage's outputs must sum back to its inputs, or a FlowConservationError
 * names exactly which stage is unbalanced). The web demo only drives it
 * through identification -> deduplication -> screening, which is exactly
 * what the module's own bundled demo does (its comment: "Modules 8-9
 * don't exist yet") — screening exclusions are a clearly-labeled
 * synthetic split of the real deduplicated count, not a fabricated
 * screening algorithm.
 */

export class FlowConservationError extends Error {}

export class PrismaFlowTracker {
  identification = new Map<string, number>();
  duplicatesRemoved = 0;
  screeningExcluded = new Map<string, number>();
  screeningIncluded: number | null = null;

  logIdentification(source: string, count: number): void {
    this.identification.set(source, (this.identification.get(source) ?? 0) + count);
  }

  logDeduplication(duplicatesRemoved: number): void {
    this.duplicatesRemoved += duplicatesRemoved;
  }

  logScreening(excludedByReason: Record<string, number>, includedCount: number): void {
    for (const [reason, count] of Object.entries(excludedByReason)) {
      this.screeningExcluded.set(reason, (this.screeningExcluded.get(reason) ?? 0) + count);
    }
    this.screeningIncluded = includedCount;
  }

  totalIdentified(): number {
    return [...this.identification.values()].reduce((a, b) => a + b, 0);
  }

  afterDedup(): number {
    return this.totalIdentified() - this.duplicatesRemoved;
  }

  totalScreeningExcluded(): number {
    return [...this.screeningExcluded.values()].reduce((a, b) => a + b, 0);
  }

  validateConservation(): void {
    if (this.screeningIncluded !== null) {
      const expected = this.afterDedup();
      const actual = this.screeningIncluded + this.totalScreeningExcluded();
      if (actual !== expected) {
        throw new FlowConservationError(
          `screening stage: ${expected} entered but ${actual} accounted for ` +
            `(${this.screeningIncluded} included + ${this.totalScreeningExcluded()} excluded)`
        );
      }
    }
  }
}
