#include "memory_bus.hpp"
#include <cstdint>
#include <iostream>
#include <stdexcept>

#ifdef require
#undef require
#endif

using namespace emu;

static void require(bool value) {
    if (!value) throw std::runtime_error("check failed");
}

static void map_all(MemoryBus& bus, std::uint8_t permissions = R | W | X) {
    for (unsigned i = 0; i < 256; ++i) bus.map_page(i, i, permissions);
}

static void endian_wrap() {
    MemoryBus bus;
    map_all(bus);
    bus.write32(0xfffe, 0x44332211);
    require(bus.read32(0xfffe) == 0x44332211);
    require(bus.read16(0xffff) == 0x3322);
}

static void precise_fault() {
    MemoryBus bus;
    bus.map_page(0, 0, R | W);
    bus.map_page(1, 1, R);
    bus.write8(0x00ff, 0xaa);
    auto before = bus.cycles();
    try {
        bus.write16(0x00ff, 0x1234);
        require(false);
    } catch (const MemoryFault& fault) {
        require(fault.address() == 0x0100);
        require(fault.access() == Access::Write);
    }
    require(bus.read8(0x00ff) == 0xaa);
    require(bus.cycles() == before + 1);
    try {
        bus.read8(0x0000, Access::Execute);
        require(false);
    } catch (const MemoryFault& fault) {
        require(fault.address() == 0 && fault.access() == Access::Execute);
    }
}

static void tlb() {
    MemoryBus bus;
    bus.map_page(0, 1, R | W);
    bus.write8(0, 0x11);
    bus.map_page(0, 2, R | W);
    bus.write8(0, 0x22);
    bus.map_page(0, 1, R | W);
    require(bus.read8(0) == 0x11);
    bus.unmap_page(0);
    try { bus.read8(0); require(false); } catch (const MemoryFault&) {}
}

static void mmio() {
    MemoryBus bus;
    map_all(bus);
    int reads = 0, writes = 0;
    unsigned last_width = 0;
    std::uint32_t cell = 0;
    bus.map_mmio(0x8000, 0x800f, {
        [&](std::uint16_t address, unsigned width) {
            require(address == 0x8002); ++reads; last_width = width; return cell;
        },
        [&](std::uint16_t address, unsigned width, std::uint32_t value) {
            require(address == 0x8002); ++writes; last_width = width; cell = value;
        },
    });
    bus.write32(0x8002, 0xdeadbeef);
    require(writes == 1 && last_width == 4);
    require(bus.read32(0x8002) == 0xdeadbeef);
    require(reads == 1 && last_width == 4 && bus.cycles() == 8);
    auto before = bus.cycles();
    try { bus.write16(0x7fff, 1); require(false); } catch (const MemoryFault& fault) {
        require(fault.address() == 0x8000);
    }
    require(writes == 1 && bus.cycles() == before);
}

static void atomic_cycles() {
    MemoryBus bus;
    map_all(bus);
    bus.write32(0x100, 41);
    auto before = bus.cycles();
    require(bus.fetch_add32(0x100, 1) == 41);
    require(bus.read32(0x100) == 42);
    require(bus.cycles() == before + 2);

    int reads = 0, writes = 0;
    std::uint32_t cell = 7;
    bus.map_mmio(0x9000, 0x9003, {
        [&](std::uint16_t, unsigned width) { require(width == 4); ++reads; return cell; },
        [&](std::uint16_t, unsigned width, std::uint32_t value) { require(width == 4); ++writes; cell = value; },
    });
    before = bus.cycles();
    require(bus.fetch_add32(0x9000, 5) == 7);
    require(cell == 12 && reads == 1 && writes == 1);
    require(bus.cycles() == before + 4);
}

int main(int, char** argv) {
    std::string mode = argv[1];
    if (mode == "endian") endian_wrap();
    else if (mode == "fault") precise_fault();
    else if (mode == "tlb") tlb();
    else if (mode == "mmio") mmio();
    else if (mode == "atomic") atomic_cycles();
    else return 2;
}
