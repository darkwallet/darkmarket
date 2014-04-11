#include <bitcoin/bitcoin.hpp>
using namespace bc;

int main()
{
    elliptic_curve_key ec;
    ec.new_keypair();
    std::cout << ec.secret() << std::endl;
    std::cout << ec.public_key() << std::endl;
    return 0;
}

