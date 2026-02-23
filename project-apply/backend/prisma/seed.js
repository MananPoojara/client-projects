const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');

const prisma = new PrismaClient();

const seedData = async () => {
  console.log('Seeding database...');

  const passwordHash = await bcrypt.hash('password123', 10);

  const head = await prisma.staff.upsert({
    where: { email: 'head@company.com' },
    update: {},
    create: {
      email: 'head@company.com',
      passwordHash,
      firstName: 'John',
      lastName: 'Smith',
      role: 'head',
      department: 'Management',
      isActive: true
    }
  });

  const senior = await prisma.staff.upsert({
    where: { email: 'senior@company.com' },
    update: {},
    create: {
      email: 'senior@company.com',
      passwordHash,
      firstName: 'Sarah',
      lastName: 'Johnson',
      role: 'senior_staff',
      department: 'Recruitment',
      isActive: true
    }
  });

  const staff = await prisma.staff.upsert({
    where: { email: 'staff@company.com' },
    update: {},
    create: {
      email: 'staff@company.com',
      passwordHash,
      firstName: 'Mike',
      lastName: 'Williams',
      role: 'staff',
      department: 'Recruitment',
      isActive: true
    }
  });

  console.log('Created staff users:');
  console.log('- head@company.com (role: head, password: password123)');
  console.log('- senior@company.com (role: senior_staff, password: password123)');
  console.log('- staff@company.com (role: staff, password: password123)');

  const candidates = await Promise.all([
    prisma.candidate.upsert({
      where: { email: 'alice.brown@email.com' },
      update: {},
      create: {
        firstName: 'Alice',
        lastName: 'Brown',
        email: 'alice.brown@email.com',
        phone: '+1234567890',
        location: 'New York, USA',
        linkedinUrl: 'https://linkedin.com/in/alicebrown',
        skills: ['JavaScript', 'React', 'Node.js', 'PostgreSQL', 'AWS'],
        experienceYears: 5,
        currentCompany: 'Tech Corp',
        currentTitle: 'Senior Developer',
        status: 'active',
        consentGdpr: true,
        createdBy: head.id
      }
    }),
    prisma.candidate.upsert({
      where: { email: 'bob.wilson@email.com' },
      update: {},
      create: {
        firstName: 'Bob',
        lastName: 'Wilson',
        email: 'bob.wilson@email.com',
        phone: '+1987654321',
        location: 'San Francisco, USA',
        linkedinUrl: 'https://linkedin.com/in/bobwilson',
        skills: ['Python', 'Django', 'Machine Learning', 'TensorFlow', 'SQL'],
        experienceYears: 7,
        currentCompany: 'DataTech Inc',
        currentTitle: 'ML Engineer',
        status: 'active',
        consentGdpr: true,
        createdBy: senior.id
      }
    }),
    prisma.candidate.upsert({
      where: { email: 'carol.davis@email.com' },
      update: {},
      create: {
        firstName: 'Carol',
        lastName: 'Davis',
        email: 'carol.davis@email.com',
        location: 'Remote',
        skills: ['Java', 'Spring Boot', 'Angular', 'MongoDB', 'Docker'],
        experienceYears: 4,
        currentCompany: 'StartupXYZ',
        currentTitle: 'Full Stack Developer',
        status: 'active',
        consentGdpr: true,
        createdBy: staff.id
      }
    })
  ]);

  console.log(`Created ${candidates.length} sample candidates`);

  const jobs = await Promise.all([
    prisma.job.upsert({
      where: { id: '00000000-0000-0000-0000-000000000001' },
      update: {},
      create: {
        id: '00000000-0000-0000-0000-000000000001',
        title: 'Senior JavaScript Developer',
        company: 'Tech Giants Inc',
        location: 'Remote',
        description: 'We are looking for an experienced JavaScript developer to join our team.',
        requirements: ['5+ years JavaScript', 'React', 'Node.js', 'TypeScript'],
        skillsRequired: ['JavaScript', 'React', 'Node.js', 'TypeScript', 'AWS'],
        salaryMin: 120000,
        salaryMax: 180000,
        sourceUrl: 'https://example.com/job/1',
        sourcePortal: 'indeed',
        jobType: 'full_time',
        remoteType: 'remote',
        status: 'active',
        postedDate: new Date()
      }
    }),
    prisma.job.upsert({
      where: { id: '00000000-0000-0000-0000-000000000002' },
      update: {},
      create: {
        id: '00000000-0000-0000-0000-000000000002',
        title: 'Python Engineer',
        company: 'Data Solutions LLC',
        location: 'New York, USA',
        description: 'Join our data engineering team to build scalable solutions.',
        requirements: ['Python', 'Django', 'PostgreSQL', 'AWS'],
        skillsRequired: ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
        salaryMin: 100000,
        salaryMax: 150000,
        sourceUrl: 'https://example.com/job/2',
        sourcePortal: 'linkedin',
        jobType: 'full_time',
        remoteType: 'hybrid',
        status: 'active',
        postedDate: new Date()
      }
    }),
    prisma.job.upsert({
      where: { id: '00000000-0000-0000-0000-000000000003' },
      update: {},
      create: {
        id: '00000000-0000-0000-0000-000000000003',
        title: 'Full Stack Developer',
        company: 'InnovateTech',
        location: 'San Francisco, USA',
        description: 'Full stack position with focus on modern web technologies.',
        requirements: ['React', 'Node.js', 'MongoDB', 'TypeScript'],
        skillsRequired: ['React', 'Node.js', 'MongoDB', 'TypeScript', 'JavaScript'],
        salaryMin: 130000,
        salaryMax: 190000,
        sourceUrl: 'https://example.com/job/3',
        sourcePortal: 'jooble',
        jobType: 'full_time',
        remoteType: 'onsite',
        status: 'active',
        postedDate: new Date()
      }
    }),
    prisma.job.upsert({
      where: { id: '00000000-0000-0000-0000-000000000004' },
      update: {},
      create: {
        id: '00000000-0000-0000-0000-000000000004',
        title: 'DevOps Engineer',
        company: 'CloudFirst Corp',
        location: 'Remote',
        description: 'Looking for a DevOps engineer to manage cloud infrastructure.',
        requirements: ['AWS', 'Kubernetes', 'Terraform', 'CI/CD'],
        skillsRequired: ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'Linux'],
        salaryMin: 140000,
        salaryMax: 200000,
        sourceUrl: 'https://example.com/job/4',
        sourcePortal: 'indeed',
        jobType: 'full_time',
        remoteType: 'remote',
        status: 'active',
        postedDate: new Date()
      }
    })
  ]);

  console.log(`Created ${jobs.length} sample jobs`);

  const applications = await Promise.all([
    prisma.application.create({
      data: {
        candidateId: candidates[0].id,
        jobId: jobs[0].id,
        staffId: staff.id,
        coverLetter: 'I am excited to apply for this position...',
        status: 'submitted',
        submittedAt: new Date()
      }
    }),
    prisma.application.create({
      data: {
        candidateId: candidates[1].id,
        jobId: jobs[1].id,
        staffId: senior.id,
        coverLetter: 'I have extensive experience in Python...',
        status: 'approved',
        reviewerId: senior.id,
        reviewedAt: new Date()
      }
    }),
    prisma.application.create({
      data: {
        candidateId: candidates[2].id,
        jobId: jobs[2].id,
        staffId: staff.id,
        status: 'pending_review'
      }
    })
  ]);

  console.log(`Created ${applications.length} sample applications`);

  console.log('Seed completed successfully!');
};

seedData()
  .catch((e) => {
    console.error('Seed error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
