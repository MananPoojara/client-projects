export class SkillSet {
  private readonly skills: Set<string>;

  constructor(skills: string[]) {
    this.skills = new Set(
      skills.map(s => s.toLowerCase().trim()).filter(s => s.length > 0)
    );
  }

  getSkills(): string[] {
    return Array.from(this.skills);
  }

  has(skill: string): boolean {
    return this.skills.has(skill.toLowerCase().trim());
  }

  add(skill: string): SkillSet {
    const newSkills = new Set(this.skills);
    newSkills.add(skill.toLowerCase().trim());
    return new SkillSet(Array.from(newSkills));
  }

  remove(skill: string): SkillSet {
    const newSkills = new Set(this.skills);
    newSkills.delete(skill.toLowerCase().trim());
    return new SkillSet(Array.from(newSkills));
  }

  matches(other: SkillSet, threshold: number = 0.5): number {
    const intersection = new Set(
      [...this.skills].filter(x => other.skills.has(x))
    ).size;
    
    const union = new Set([...this.skills, ...other.skills]).size;
    
    return union > 0 ? (intersection / union) * 100 : 0;
  }

  getMatchPercentage(requiredSkills: string[]): number {
    const required = new SkillSet(requiredSkills);
    return this.matches(required);
  }

  equals(other: SkillSet): boolean {
    if (this.skills.size !== other.skills.size) return false;
    return [...this.skills].every(s => other.skills.has(s));
  }
}
