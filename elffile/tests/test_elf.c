#include <stdio.h>

struct elf_test;

struct elf_test{
    char *g;
    char v;
    int x;
    int y;
};

const char *g_ = "This is a really long string somewhere in .data.\n";



void do_something(struct elf_test *t){

    printf("I am doing something with g_ he he. %08x\n",(g_) );
    printf("I am doing something with &g_ he he. %08x\n",&(g_) );
    printf("I am doing something with t he he. %08x\n",t );
    printf("I am doing something with t->v he he. %08x\n",&(t->v) );
    printf("I am doing something with t->g he he. %08x\n",&(t->g) );
    printf("I am doing something with t->x he he. %08x\n",&(t->x) );
}
int main(){
    
    struct elf_test t;
    int y, x, j;
    for (j = 0; j < 10; j++){
        t.x = 10;
        t.y = j;
        t.g = g_;
        t.v = '&';
        do_something(&t);
        printf("%x %c %x = %x\n", t.x, t.v, t.y, t.x & t.y);
    }
    printf("Test is complete\n");
    //printf("%s",g);
    return 0;
}   
