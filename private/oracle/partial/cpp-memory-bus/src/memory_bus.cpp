#include "memory_bus.hpp"

namespace emu {
MemoryFault::MemoryFault(std::uint16_t address, Access access, const char* message)
    : std::runtime_error(message), address_(address), access_(access) {}
void MemoryBus::map_page(std::uint8_t v, std::uint8_t p, std::uint8_t permissions) {
    pages_[v] = {true, p, permissions}; tlb_[v] = {};
}
void MemoryBus::unmap_page(std::uint8_t v) { pages_[v] = {}; tlb_[v] = {}; }
void MemoryBus::map_mmio(std::uint16_t first, std::uint16_t last, MmioDevice device) {
    has_mmio_ = true; mmio_first_ = first; mmio_last_ = last; mmio_ = std::move(device);
}
std::uint16_t MemoryBus::translate(std::uint16_t address, Access access) {
    auto page = static_cast<std::uint8_t>(address >> 8);
    auto mapping = tlb_[page].valid ? tlb_[page] : (tlb_[page] = pages_[page]);
    auto required = access == Access::Read ? R : access == Access::Write ? W : X;
    if (!mapping.valid) throw MemoryFault(address, access, "unmapped");
    if (!(mapping.permissions & required)) throw MemoryFault(address, access, "protection");
    return static_cast<std::uint16_t>((mapping.physical << 8) | (address & 0xff));
}
std::uint8_t MemoryBus::read8(std::uint16_t a, Access access) { ++cycles_; return ram_[translate(a, access)]; }
std::uint16_t MemoryBus::read16(std::uint16_t a, Access access) { return read8(a, access) | (read8(a + 1, access) << 8); }
std::uint32_t MemoryBus::read32(std::uint16_t a, Access access) { return read16(a, access) | (std::uint32_t(read16(a + 2, access)) << 16); }
void MemoryBus::write8(std::uint16_t a, std::uint8_t v) { ++cycles_; ram_[translate(a, Access::Write)] = v; }
void MemoryBus::write16(std::uint16_t a, std::uint16_t v) { write8(a, v); write8(a + 1, v >> 8); }
void MemoryBus::write32(std::uint16_t a, std::uint32_t v) { write16(a, v); write16(a + 2, v >> 16); }
std::uint32_t MemoryBus::fetch_add32(std::uint16_t a, std::uint32_t v) { auto old = read32(a); write32(a, old + v); return old; }
}
