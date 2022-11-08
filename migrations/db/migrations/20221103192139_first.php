<?php

use Phinx\Migration\AbstractMigration;

class First extends AbstractMigration
{
    public function up(){

        $user = $this->table('users');
        $user
            ->addColumn('username', 'string',   ['limit' => 30,     'null' => false])
            ->addColumn('email',    'string',   ['limit' => 40,     'null' => false])
            ->addColumn('password', 'string',   ['limit' => 200,    'null' => false])
            ->addColumn('role',     'enum',     [                   'null' => false,   'values' => ['admin', 'user']])
            ->addColumn('active',   'integer',  [                   'null' => false])
            ->addColumn('token',    'string',   ['limit' => 40,     'null' => false])
            ->create();

        $risk = $this->table('risks');
        $risk
            ->addColumn('name',     'string',   ['limit' => 300,    'null' => false])
            ->addColumn('descript', 'string',   ['limit' => 600,    'null' => false])
            ->addColumn('category', 'string',   ['limit' => 100,    'null' => false])
            ->addColumn('public',   'boolean',   [                   'null' => false])
            ->addColumn('user_id',  'integer',  [                   'null' => true])
            ->addForeignKey('user_id','users','id',['delete'=> 'CASCADE', 'update'=> 'CASCADE'])
            ->create();
        
        $table = $this->table('tables');
        $table
            ->addColumn('user_id',  'integer',  [                    'null' => false])
            ->addColumn('name',     'string',   ['limit' => 100,     'null' => false,])
            ->addForeignKey('user_id','users','id',['delete'=> 'CASCADE', 'update'=> 'CASCADE'])
            ->create();

        $trow = $this->table('trows');
        $trow
            ->addColumn('table_id', 'integer',  [                    'null' => false])
            ->addColumn('prob',     'enum',     [                    'null' => false,   'values' => ['1', '2', '3', '4', '5']])
            ->addColumn('impact',   'enum',     [                    'null' => false,   'values' => ['1', '2', '3', '4', '5']])
            ->addColumn('result',   'enum',     [                    'null' => false,   'values' => ['low', 'moderate', 'high', 'extreme']])
            ->addColumn('solution', 'string',   ['limit' => 600,     'null' => true,])
            ->addForeignKey('table_id','tables','id',['delete'=> 'CASCADE', 'update'=> 'CASCADE'])
            ->create();
    }


    public function down(){

        $this->execute('DELETE FROM trows');
        $this->execute('DELETE FROM tables');
        $this->execute('DELETE FROM risks');
        $this->execute('DELETE FROM users');
        
        $this->table('trows')->drop()->save();
        $this->table('tables')->drop()->save();
        $this->table('risks')->drop()->save();
        $this->table('users')->drop()->save();
    }
}
