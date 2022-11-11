<?php

use Phinx\Migration\AbstractMigration;

class BoehmData extends AbstractMigration
{
    public function up()
    {
        $users = $this->table('users');
        $singleRow = [
            'id' => 1,
            'username'  => 'Boehm',
            'email'     => 'pointarisk@gmail.com',
            'password'  => 'TryToHackThis',
            'role'      => 'user',
            'token'     => 'AAAAA',
            'active'    => 1
        ];
        $users->insert($singleRow)->saveData();

        $risks = $this->table('risks');
        $rows = [
            [
                'id'        => "1",
                'name'      => "Personnel Shortfalls",
                'category'  => "Personal",
                'descript'  => "Staffing with top talent; job matching;team-building; morale-building; cross-training; prescheduling key people.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "2",
                'name'      => "Unrealistic Schedules and Budgets",
                'category'  => "Schedules",
                'descript'  => "Detailed, multisource cost and schedule estimation; design to cost; incremental development; software reuse; requirements scrubbing.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "3",
                'name'      => "Developing the wrong software functions",
                'category'  => "Functions",
                'descript'  => "Organizational analysis; mission analysis; operational concept formulation; user surveys; prototyping; early users’ manuals.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "4",
                'name'      => "Developing the wrong user interface",
                'category'  => "Interface",
                'descript'  => "Prototyping; scenarios; task analysis.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "5",
                'name'      => "Gold-plating. Requirements scrubbing",
                'category'  => "Requirements",
                'descript'  => "prototyping; cost-benefit analysis; design to cost.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "6",
                'name'      => "Continuing stream of requirements changes",
                'category'  => "Requirements",
                'descript'  => "High change threshold; information-hiding; incremental development (defer changes to later increments)",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "7",
                'name'      => "Shortfalls in externally-performed tasks",
                'category'  => "Shortfalls",
                'descript'  => "Reference-checking; pre-award audits; award-fee contracts; competitive design or prototyping; team-building.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "8",
                'name'      => "Shortfalls in externally-furnished components",
                'category'  => "Shortfalls",
                'descript'  => "Benchmarking; inspections; reference checking; compatibility analysis.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "9",
                'name'      => "Real-time performance shortfalls",
                'category'  => "Shortfalls",
                'descript'  => " Simulation; benchmarking; modelling; prototyping; instrumentation; tuning.",
                'public'    => "1",
                'user_id'   => "1",
            ],
            [
                'id'        => "10",
                'name'      => "Straining computer science capabilities",
                'category'  => "Capabilities",
                'descript'  => "Technical analysis; cost-benefit analysis; prototyping; reference checking.",
                'public'    => "1",
                'user_id'   => "1",
            ],
        ];
        $risks->insert($rows)->saveData();
    }

    public function down()
    {
        $this->execute('DELETE FROM users where id=1');
    }
}
