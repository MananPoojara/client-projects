export class MatchScore {
  private readonly value: number;

  constructor(score: number) {
    if (score < 0 || score > 100) {
      throw new Error('Match score must be between 0 and 100');
    }
    this.value = score;
  }

  getValue(): number {
    return this.value;
  }

  isStrongMatch(): boolean {
    return this.value >= 70;
  }

  isGoodMatch(): boolean {
    return this.value >= 50 && this.value < 70;
  }

  isWeakMatch(): boolean {
    return this.value > 0 && this.value < 50;
  }

  static calculate(candidateSkills: string[], jobSkills: string[]): MatchScore {
    if (candidateSkills.length === 0 || jobSkills.length === 0) {
      return new MatchScore(0);
    }

    const candidateSet = new Set(candidateSkills.map(s => s.toLowerCase()));
    const jobSet = new Set(jobSkills.map(s => s.toLowerCase()));

    const matchingSkills = [...candidateSet].filter(s => jobSet.has(s)).length;
    const score = (matchingSkills / jobSet.size) * 100;

    return new MatchScore(Math.round(score));
  }

  equals(other: MatchScore): boolean {
    return this.value === other.value;
  }

  compareTo(other: MatchScore): number {
    return this.value - other.value;
  }
}
