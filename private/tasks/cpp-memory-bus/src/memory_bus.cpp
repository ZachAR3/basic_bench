#include "memory_bus.hpp"

namespace emu {

MemoryFault::MemoryFault(std::uint16_t address, Access access, const char* message)
    : std::runtime_error(message), address_(address), access_(access) {}

void MemoryBus::map_page(std::uint8_t virtual_page, std::uint8_t physical_page, std::uint8_t permissions) {
    pages_[virtual_page] = {true, physical_page, permissions};
}

void MemoryBus::unmap_page(std::uint8_t virtual_page) {
    pages_[virtual_page] = {};
}

void MemoryBus::map_mmio(std::uint16_t first, std::uint16_t last, MmioDevice device) {
    has_mmio_ = true; mmio_first_ = first; mmio_last_ = last; mmio_ = std::move(device);
}

std::uint16_t MemoryBus::translate(std::uint16_t address, Access) {
    auto page = static_cast<std::uint8_t>(address >> 8);
    auto mapping = tlb_[page].valid ? tlb_[page] : (tlb_[page] = pages_[page]);
    if (!mapping.valid) throw MemoryFault(address, Access::Read, "unmapped");
    return static_cast<std::uint16_t>((mapping.physical << 8) | (address & 0xff));
}

std::uint8_t MemoryBus::read8(std::uint16_t address, Access access) {
    ++cycles_;
    if (has_mmio_ && address >= mmio_first_ && address <= mmio_last_)
        return static_cast<std::uint8_t>(mmio_.read(address, 1));
    return ram_[translate(address, access)];
}
std::uint16_t MemoryBus::read16(std::uint16_t address, Access access) {
    return read8(address, access) | (read8(address + 1, access) << 8);
}
std::uint32_t MemoryBus::read32(std::uint16_t address, Access access) {
    return read16(address, access) | (std::uint32_t(read16(address + 2, access)) << 16);
}
void MemoryBus::write8(std::uint16_t address, std::uint8_t value) {
    ++cycles_;
    if (has_mmio_ && address >= mmio_first_ && address <= mmio_last_) {
        mmio_.write(address, 1, value); return;
    }
    ram_[translate(address, Access::Write)] = value;
}
void MemoryBus::write16(std::uint16_t address, std::uint16_t value) {
    write8(address, value); write8(address + 1, value >> 8);
}
void MemoryBus::write32(std::uint16_t address, std::uint32_t value) {
    write16(address, value); write16(address + 2, value >> 16);
}
std::uint32_t MemoryBus::fetch_add32(std::uint16_t address, std::uint32_t value) {
    auto before = read32(address); write32(address, before + value); return before;
}

}
